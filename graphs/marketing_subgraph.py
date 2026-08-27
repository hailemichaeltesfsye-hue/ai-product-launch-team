import logging
from typing import Any, Dict
from langgraph.graph import END, START, StateGraph
from agents.content import content_agent
from agents.marketing_manager import (
    marketing_manager_aggregator_agent,
    marketing_manager_planner_agent,
)
from agents.research import research_agent
from state.schemas import ContentPlan, MarketingReport, ResearchReport, SubTask, TaskDecomposition
from state.state import HierarchicalState
from state.handoffs import record_handoffs, record_handoff

logger = logging.getLogger(__name__)


def marketing_decompose_node(state: HierarchicalState) -> Dict[str, Any]:
    """Marketing Manager node: turns the CEO's marketing_directive into
    subtasks for ResearchAgent and ContentAgent. The resulting subtask
    instructions are stashed on the state via a private key convention so
    research_node/content_node can find their assigned instructions."""
    directive = state.get("marketing_directive", "") or ""
    logger.info("Marketing Manager: Decomposing directive into subtasks.")

    prompt = f"Marketing Directive from CEO: {directive}\n\nDecompose this into subtasks for ResearchAgent and ContentAgent."

    try:
        result = marketing_manager_planner_agent.run_sync(prompt)
        decomposition: TaskDecomposition = result.output
        logger.info("Marketing Manager decomposition complete with %d subtasks.", len(decomposition.subtasks))
        return {
            "marketing_decomposition": decomposition,
            **record_handoffs(
                ("Marketing Manager", "ResearchAgent", "Marketing Manager assigned market research."),
                ("Marketing Manager", "ContentAgent", "Marketing Manager assigned launch content."),
            ),
        }
    except Exception as exc:
        err_msg = f"Marketing Manager decomposition failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "marketing_decomposition": TaskDecomposition(
                plan_summary="Fallback plan due to decomposition error.",
                subtasks=[
                    SubTask(
                        id="fallback_research",
                        agent_type="research",
                        title="Market Research",
                        instructions=f"Analyze market opportunities for: {directive}",
                    ),
                    SubTask(
                        id="fallback_content",
                        agent_type="content",
                        title="Messaging & Content Strategy",
                        instructions=f"Formulate messaging strategy for: {directive}",
                    ),
                ],
            ),
            "errors": [err_msg],
        }


def research_node(state: HierarchicalState) -> Dict[str, Any]:
    """ResearchAgent node: conducts market and competitor research."""
    decomposition = state.get("marketing_decomposition")
    directive = state.get("marketing_directive", "") or ""

    subtask = next(
        (t for t in decomposition.subtasks if t.agent_type == "research"), None
    ) if decomposition else None

    instructions = subtask.instructions if subtask else f"Conduct market research for: {directive}"
    title = subtask.title if subtask else "Market Research"

    logger.info("ResearchAgent executing subtask: %s", title)
    prompt = f"Subtask Title: {title}\nInstructions: {instructions}"

    try:
        result = research_agent.run_sync(prompt)
        report: ResearchReport = result.output
        logger.info("ResearchAgent completed successfully.")
        return {
            "research_output": report,
            **record_handoff("ResearchAgent", "ContentAgent", "Research deliverable is ready for content strategy."),
        }
    except Exception as exc:
        err_msg = f"ResearchAgent execution failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "research_output": ResearchReport(
                summary=f"Research could not be completed automatically for: {directive}",
                market_trends=["AI adoption", "Market expansion"],
                competitors=["Existing market alternatives"],
                key_findings=[f"Encountered error: {exc}"],
                opportunities=["Requires manual domain assessment"],
            ),
            "errors": [err_msg],
        }


def content_node(state: HierarchicalState) -> Dict[str, Any]:
    """ContentAgent node: crafts messaging and content strategy, informed by research."""
    decomposition = state.get("marketing_decomposition")
    directive = state.get("marketing_directive", "") or ""
    research_output = state.get("research_output")

    subtask = next(
        (t for t in decomposition.subtasks if t.agent_type == "content"), None
    ) if decomposition else None

    instructions = subtask.instructions if subtask else f"Develop content and messaging for: {directive}"
    title = subtask.title if subtask else "Content Strategy"

    research_context = ""
    if research_output:
        research_context = (
            f"\nResearch Findings:\n"
            f"- Summary: {research_output.summary}\n"
            f"- Key Trends: {', '.join(research_output.market_trends)}\n"
            f"- Opportunities: {', '.join(research_output.opportunities)}\n"
        )

    logger.info("ContentAgent executing subtask: %s", title)
    prompt = f"Subtask Title: {title}\nInstructions: {instructions}\n{research_context}"

    try:
        result = content_agent.run_sync(prompt)
        content_plan: ContentPlan = result.output
        logger.info("ContentAgent completed successfully.")
        return {
            "content_output": content_plan,
            **record_handoff("ContentAgent", "Marketing Manager", "Content plan is complete and ready for manager synthesis."),
        }
    except Exception as exc:
        err_msg = f"ContentAgent execution failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "content_output": ContentPlan(
                headline=f"Launch Campaign for {directive}",
                core_messaging=f"Fallback positioning: {directive}",
                target_channels=["Direct", "Social", "Email"],
                content_pieces=["Product Overview", "Launch Announcement"],
                call_to_action="Get Started Today",
            ),
            "errors": [err_msg],
        }


def marketing_aggregate_node(state: HierarchicalState) -> Dict[str, Any]:
    """Marketing Manager node: synthesizes ResearchReport + ContentPlan into
    a single MarketingReport to hand up to the CEO."""
    directive = state.get("marketing_directive", "") or ""
    research_output = state.get("research_output")
    content_output = state.get("content_output")

    logger.info("Marketing Manager: Synthesizing MarketingReport...")
    prompt = (
        f"Marketing Directive:\n{directive}\n\n"
        f"Research Report:\n{research_output.model_dump_json(indent=2) if research_output else 'No research output'}\n\n"
        f"Content Plan:\n{content_output.model_dump_json(indent=2) if content_output else 'No content output'}\n\n"
        f"Synthesize these into a MarketingReport."
    )

    try:
        result = marketing_manager_aggregator_agent.run_sync(prompt)
        marketing_report: MarketingReport = result.output
        logger.info("Marketing Manager synthesis complete.")
        return {
            "marketing_report": marketing_report,
            **record_handoff("Marketing Manager", "CEO", "Marketing report is complete and ready for executive synthesis."),
        }
    except Exception as exc:
        err_msg = f"Marketing Manager synthesis failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "marketing_report": MarketingReport(
                summary=f"Marketing synthesis unavailable for: {directive}",
                market_positioning="Fallback positioning pending manual review.",
                key_research_insights=[research_output.summary] if research_output else [],
                messaging_summary=content_output.core_messaging if content_output else "Not available.",
                recommended_channels=content_output.target_channels if content_output else [],
            ),
            "errors": [err_msg],
        }


# Build the Marketing Manager subgraph.
# Sequential by design: research -> content -> aggregate. Content depends on
# research output (single predecessor), and aggregate has a single
# predecessor (content) - so this topology cannot suffer the fan-in
# duplicate-firing bug regardless of timing.
_marketing_workflow = StateGraph(HierarchicalState)
_marketing_workflow.add_node("decompose", marketing_decompose_node)
_marketing_workflow.add_node("research", research_node)
_marketing_workflow.add_node("content", content_node)
_marketing_workflow.add_node("aggregate", marketing_aggregate_node)

_marketing_workflow.add_edge(START, "decompose")
_marketing_workflow.add_edge("decompose", "research")
_marketing_workflow.add_edge("research", "content")
_marketing_workflow.add_edge("content", "aggregate")
_marketing_workflow.add_edge("aggregate", END)

marketing_subgraph = _marketing_workflow.compile()