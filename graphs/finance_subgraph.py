import logging
from typing import Any, Dict
from langgraph.graph import END, START, StateGraph
from agents.cost import cost_agent
from agents.finance_manager import (
    finance_manager_aggregator_agent,
    finance_manager_planner_agent,
)
from agents.pricing import pricing_agent
from state.schemas import CostAssessment, FinanceReport, PricingStrategy, SubTask, TaskDecomposition
from state.state import HierarchicalState
from state.handoffs import record_handoffs, record_handoff

logger = logging.getLogger(__name__)


def finance_decompose_node(state: HierarchicalState) -> Dict[str, Any]:
    """Finance Manager node: turns the CEO's finance_directive into subtasks
    for CostAgent and PricingAgent."""
    directive = state.get("finance_directive", "") or ""
    logger.info("Finance Manager: Decomposing directive into subtasks.")

    prompt = f"Finance Directive from CEO: {directive}\n\nDecompose this into subtasks for CostAgent and PricingAgent."

    try:
        result = finance_manager_planner_agent.run_sync(prompt)
        decomposition: TaskDecomposition = result.output
        logger.info("Finance Manager decomposition complete with %d subtasks.", len(decomposition.subtasks))
        return {
            "finance_decomposition": decomposition,
            **record_handoffs(
                ("Finance Manager", "CostAgent", "Finance Manager assigned cost analysis."),
                ("Finance Manager", "PricingAgent", "Finance Manager assigned pricing strategy."),
            ),
        }
    except Exception as exc:
        err_msg = f"Finance Manager decomposition failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "finance_decomposition": TaskDecomposition(
                plan_summary="Fallback plan due to decomposition error.",
                subtasks=[
                    SubTask(
                        id="fallback_cost",
                        agent_type="cost",
                        title="Cost Analysis",
                        instructions=f"Evaluate setup and recurring costs for: {directive}",
                    ),
                    SubTask(
                        id="fallback_pricing",
                        agent_type="pricing",
                        title="Pricing Strategy",
                        instructions=f"Design a pricing strategy for: {directive}",
                    ),
                ],
            ),
            "errors": [err_msg],
        }


def cost_node(state: HierarchicalState) -> Dict[str, Any]:
    """CostAgent node: estimates setup costs, recurring costs, break-even.
    Runs in parallel with pricing_node - both are 1 hop from finance_decompose,
    so they complete in the same superstep and finance_aggregate_node fires
    exactly once (equal-depth fan-in, verified by test_finance_subgraph.py)."""
    decomposition = state.get("finance_decomposition")
    directive = state.get("finance_directive", "") or ""

    subtask = next(
        (t for t in decomposition.subtasks if t.agent_type == "cost"), None
    ) if decomposition else None

    instructions = subtask.instructions if subtask else f"Evaluate costs for: {directive}"
    title = subtask.title if subtask else "Cost Analysis"

    logger.info("CostAgent executing subtask: %s", title)
    prompt = f"Subtask Title: {title}\nInstructions: {instructions}"

    try:
        result = cost_agent.run_sync(prompt)
        cost_assessment: CostAssessment = result.output
        logger.info("CostAgent completed successfully.")
        return {
            "cost_output": cost_assessment,
            **record_handoff("CostAgent", "Finance Manager", "Cost assessment is ready for manager synthesis."),
        }
    except Exception as exc:
        err_msg = f"CostAgent execution failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "cost_output": CostAssessment(
                estimated_setup_cost="$50,000 - $100,000 estimated initial spend",
                recurring_costs=["Infrastructure / Cloud", "Operations"],
                break_even_timeline="12-18 months",
                cost_risks=[f"Calculation variance: {exc}"],
            ),
            "errors": [err_msg],
        }


def pricing_node(state: HierarchicalState) -> Dict[str, Any]:
    """PricingAgent node: designs pricing model, tiers, and revenue streams.
    Runs in parallel with cost_node (see cost_node docstring)."""
    decomposition = state.get("finance_decomposition")
    directive = state.get("finance_directive", "") or ""

    subtask = next(
        (t for t in decomposition.subtasks if t.agent_type == "pricing"), None
    ) if decomposition else None

    instructions = subtask.instructions if subtask else f"Design a pricing strategy for: {directive}"
    title = subtask.title if subtask else "Pricing Strategy"

    logger.info("PricingAgent executing subtask: %s", title)
    prompt = f"Subtask Title: {title}\nInstructions: {instructions}"

    try:
        result = pricing_agent.run_sync(prompt)
        pricing_strategy: PricingStrategy = result.output
        logger.info("PricingAgent completed successfully.")
        return {
            "pricing_output": pricing_strategy,
            **record_handoff("PricingAgent", "Finance Manager", "Pricing strategy is ready for manager synthesis."),
        }
    except Exception as exc:
        err_msg = f"PricingAgent execution failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "pricing_output": PricingStrategy(
                pricing_model="Tiered SaaS subscription (fallback default)",
                pricing_tiers=["Basic $29/mo", "Pro $79/mo"],
                revenue_streams=["Subscription revenue"],
                pricing_risks=[f"Calculation variance: {exc}"],
            ),
            "errors": [err_msg],
        }


def finance_aggregate_node(state: HierarchicalState) -> Dict[str, Any]:
    """Finance Manager node: synthesizes CostAssessment + PricingStrategy
    into a single FinanceReport to hand up to the CEO."""
    directive = state.get("finance_directive", "") or ""
    cost_output = state.get("cost_output")
    pricing_output = state.get("pricing_output")

    logger.info("Finance Manager: Synthesizing FinanceReport...")
    prompt = (
        f"Finance Directive:\n{directive}\n\n"
        f"Cost Assessment:\n{cost_output.model_dump_json(indent=2) if cost_output else 'No cost output'}\n\n"
        f"Pricing Strategy:\n{pricing_output.model_dump_json(indent=2) if pricing_output else 'No pricing output'}\n\n"
        f"Synthesize these into a FinanceReport."
    )

    try:
        result = finance_manager_aggregator_agent.run_sync(prompt)
        finance_report: FinanceReport = result.output
        logger.info("Finance Manager synthesis complete.")
        return {
            "finance_report": finance_report,
            **record_handoff("Finance Manager", "CEO", "Finance report is complete and ready for executive synthesis."),
        }
    except Exception as exc:
        err_msg = f"Finance Manager synthesis failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "finance_report": FinanceReport(
                summary=f"Finance synthesis unavailable for: {directive}",
                cost_overview=cost_output.estimated_setup_cost if cost_output else "Not available.",
                pricing_overview=pricing_output.pricing_model if pricing_output else "Not available.",
                financial_risks=(cost_output.cost_risks if cost_output else [])
                + (pricing_output.pricing_risks if pricing_output else []),
            ),
            "errors": [err_msg],
        }


# Build the Finance Manager subgraph.
# Cost and Pricing run in TRUE PARALLEL (both 1 hop from finance_decompose),
# then converge directly on finance_aggregate. Equal-depth fan-in is safe
# from LangGraph's Pregel scheduling perspective (both predecessors complete
# in the same superstep) - verified by an explicit call-count regression
# test rather than assumed.
_finance_workflow = StateGraph(HierarchicalState)
_finance_workflow.add_node("decompose", finance_decompose_node)
_finance_workflow.add_node("cost", cost_node)
_finance_workflow.add_node("pricing", pricing_node)
_finance_workflow.add_node("aggregate", finance_aggregate_node)

_finance_workflow.add_edge(START, "decompose")
_finance_workflow.add_edge("decompose", "cost")
_finance_workflow.add_edge("decompose", "pricing")
_finance_workflow.add_edge("cost", "aggregate")
_finance_workflow.add_edge("pricing", "aggregate")
_finance_workflow.add_edge("aggregate", END)

finance_subgraph = _finance_workflow.compile()