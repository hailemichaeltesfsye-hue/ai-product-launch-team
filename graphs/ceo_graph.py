import logging
from typing import Any, Dict
from langgraph.graph import END, START, StateGraph
from agents.ceo import ceo_aggregator_agent, ceo_planner_agent
from graphs.finance_subgraph import finance_subgraph
from graphs.marketing_subgraph import marketing_subgraph
from state.schemas import ExecutiveReport
from state.state import HierarchicalState
from state.handoffs import record_handoff, record_handoffs

logger = logging.getLogger(__name__)


def ceo_decompose_node(state: HierarchicalState) -> Dict[str, Any]:
    """CEO node: turns the user's request into a marketing_directive and a
    finance_directive for the two managers."""
    user_request = state.get("user_request", "")
    logger.info("CEO: Decomposing user request into manager directives.")

    prompt = f"User Request: {user_request}\n\nProduce directives for the Marketing Manager and Finance Manager."

    try:
        result = ceo_planner_agent.run_sync(prompt)
        decomposition = result.output
        logger.info("CEO decomposition complete.")
        return {
            **record_handoffs(
                ("CEO", "Marketing Manager", "CEO delegated the marketing directive."),
                ("CEO", "Finance Manager", "CEO delegated the finance directive."),
            ),
            "marketing_directive": decomposition.marketing_directive,
            "finance_directive": decomposition.finance_directive,
        }
    except Exception as exc:
        err_msg = f"CEO decomposition failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            **record_handoff("CEO", "Marketing Manager", "CEO used fallback delegation after planning failed."),
            "marketing_directive": f"Develop a marketing strategy for: {user_request}",
            "finance_directive": f"Develop a financial plan for: {user_request}",
            "errors": [err_msg],
        }


def marketing_subgraph_node(state: HierarchicalState) -> Dict[str, Any]:
    """CEO-graph node: invokes the compiled Marketing Manager subgraph on
    the same shared HierarchicalState and merges its result back. Runs in
    parallel with finance_subgraph_node (both 1 hop from ceo_decompose).

    IMPORTANT: the subgraph is given a *copy* of the parent state with
    "errors" reset to []. If we passed the parent's already-accumulated
    errors straight through, the subgraph's own final "errors" list would
    contain them too, and returning that whole list would double-count them
    against the parent's operator.add reducer (once from the parent's own
    state, once again from this branch re-returning what it inherited)."""
    logger.info("Invoking Marketing Manager subgraph...")
    subgraph_input = {**state, "errors": [], "handoff_history": []}
    result = marketing_subgraph.invoke(subgraph_input)
    # Only propagate the keys this branch is responsible for, to avoid
    # accidentally clobbering keys the finance branch is concurrently writing.
    output: Dict[str, Any] = {
        "research_output": result.get("research_output"),
        "content_output": result.get("content_output"),
        "marketing_report": result.get("marketing_report"),
        "marketing_decomposition": result.get("marketing_decomposition"),
    }
    output["handoff_history"] = result.get("handoff_history", [])
    if result.get("errors"):
        output["errors"] = result["errors"]
    return output


def finance_subgraph_node(state: HierarchicalState) -> Dict[str, Any]:
    """CEO-graph node: invokes the compiled Finance Manager subgraph on the
    same shared HierarchicalState and merges its result back. Runs in
    parallel with marketing_subgraph_node (both 1 hop from ceo_decompose).

    See marketing_subgraph_node's docstring for why "errors" is reset to []
    before invoking the subgraph."""
    logger.info("Invoking Finance Manager subgraph...")
    subgraph_input = {**state, "errors": [], "handoff_history": []}
    result = finance_subgraph.invoke(subgraph_input)
    output: Dict[str, Any] = {
        "cost_output": result.get("cost_output"),
        "pricing_output": result.get("pricing_output"),
        "finance_report": result.get("finance_report"),
        "finance_decomposition": result.get("finance_decomposition"),
    }
    output["handoff_history"] = result.get("handoff_history", [])
    if result.get("errors"):
        output["errors"] = result["errors"]
    return output


def ceo_aggregate_node(state: HierarchicalState) -> Dict[str, Any]:
    """CEO node: synthesizes MarketingReport + FinanceReport into the final
    ExecutiveReport."""
    user_request = state.get("user_request", "")
    marketing_report = state.get("marketing_report")
    finance_report = state.get("finance_report")

    logger.info("CEO: Synthesizing final ExecutiveReport...")
    prompt = (
        f"Original User Request:\n{user_request}\n\n"
        f"Marketing Report:\n{marketing_report.model_dump_json(indent=2) if marketing_report else 'No marketing report'}\n\n"
        f"Finance Report:\n{finance_report.model_dump_json(indent=2) if finance_report else 'No finance report'}\n\n"
        f"Synthesize these into a final ExecutiveReport."
    )

    try:
        result = ceo_aggregator_agent.run_sync(prompt)
        executive_report: ExecutiveReport = result.output
        logger.info("CEO synthesis complete.")
        return {
            "final_response": executive_report,
            **record_handoff("Marketing Manager", "CEO", "Manager reports were synthesized into the executive report."),
        }
    except Exception as exc:
        err_msg = f"CEO synthesis failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            **record_handoff("Marketing Manager", "CEO", "CEO received a fallback executive synthesis."),
            "final_response": ExecutiveReport(
                executive_summary=f"Consolidated strategy summary for: {user_request}",
                strategic_analysis="Automated synthesis encountered an error; fallback summary generated.",
                marketing_highlights=marketing_report.summary if marketing_report else "Marketing report not available.",
                finance_highlights=finance_report.summary if finance_report else "Finance report not available.",
                action_items=["Review manager reports", "Refine business model"],
            ),
            "errors": [err_msg],
        }


# Build the top-level CEO graph.
# marketing_subgraph_node and finance_subgraph_node are both 1 hop from
# ceo_decompose (equal-depth parallel fan-in into ceo_aggregate) - the same
# safe pattern verified for cost/pricing in finance_subgraph.py.
_ceo_workflow = StateGraph(HierarchicalState)
_ceo_workflow.add_node("decompose", ceo_decompose_node)
_ceo_workflow.add_node("marketing", marketing_subgraph_node)
_ceo_workflow.add_node("finance", finance_subgraph_node)
_ceo_workflow.add_node("aggregate", ceo_aggregate_node)

_ceo_workflow.add_edge(START, "decompose")
_ceo_workflow.add_edge("decompose", "marketing")
_ceo_workflow.add_edge("decompose", "finance")
_ceo_workflow.add_edge("marketing", "aggregate")
_ceo_workflow.add_edge("finance", "aggregate")
_ceo_workflow.add_edge("aggregate", END)

ceo_graph = _ceo_workflow.compile()