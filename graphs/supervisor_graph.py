import json
import logging
from typing import Any, Dict, List
from langgraph.graph import END, START, StateGraph
from agents.content import content_agent
from agents.financial import financial_agent
from agents.research import research_agent
from agents.supervisor import supervisor_aggregator_agent, supervisor_planner_agent
from state.schemas import (
    ConsolidatedReport,
    ContentPlan,
    FinancialAssessment,
    ResearchReport,
    SubTask,
    TaskDecomposition,
)
from state.state import SupervisorGraphState

logger = logging.getLogger(__name__)


def decompose_node(state: SupervisorGraphState) -> Dict[str, Any]:
    """Supervisor node: Decomposes the user request into specialist subtasks."""
    user_request = state.get("user_request", "")
    logger.info("Supervisor Planner: Decomposing user request: %s", user_request)
    
    prompt = f"User Request: {user_request}\n\nDecompose this into 3 specific subtasks for ResearchAgent, ContentAgent, and FinancialAgent."
    
    try:
        result = supervisor_planner_agent.run_sync(prompt)
        decomposition: TaskDecomposition = result.output
        logger.info("Decomposition complete with %d subtasks.", len(decomposition.subtasks))
        return {"decomposition": decomposition}
    except Exception as exc:
        err_msg = f"Decomposition failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "decomposition": TaskDecomposition(
                plan_summary="Fallback plan due to decomposition error.",
                subtasks=[
                    SubTask(
                        id="fallback_research",
                        agent_type="research",
                        title="Market Research",
                        instructions=f"Analyze market opportunities for: {user_request}",
                    ),
                    SubTask(
                        id="fallback_content",
                        agent_type="content",
                        title="Messaging & Content Strategy",
                        instructions=f"Formulate messaging strategy for: {user_request}",
                    ),
                    SubTask(
                        id="fallback_financial",
                        agent_type="financial",
                        title="Financial Modeling",
                        instructions=f"Evaluate cost and revenue model for: {user_request}",
                    ),
                ],
            ),
            "errors": [err_msg],
        }


def research_node(state: SupervisorGraphState) -> Dict[str, Any]:
    """ResearchAgent node: Conducts market and competitor research."""
    decomposition = state.get("decomposition")
    user_request = state.get("user_request", "")
    
    subtask = next(
        (t for t in decomposition.subtasks if t.agent_type == "research"),
        None,
    ) if decomposition else None

    instructions = subtask.instructions if subtask else f"Conduct market research for: {user_request}"
    title = subtask.title if subtask else "Market Research"
    
    logger.info("ResearchAgent executing subtask: %s", title)
    prompt = f"Topic / Request: {user_request}\nSubtask Title: {title}\nInstructions: {instructions}"
    
    try:
        result = research_agent.run_sync(prompt)
        report: ResearchReport = result.output
        logger.info("ResearchAgent completed successfully.")
        return {"research_output": report}
    except Exception as exc:
        err_msg = f"ResearchAgent execution failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "research_output": ResearchReport(
                summary=f"Research could not be completed automatically for: {user_request}",
                market_trends=["AI adoption", "Market expansion"],
                competitors=["Existing market alternatives"],
                key_findings=[f"Encountered error: {exc}"],
                opportunities=["Requires manual domain assessment"],
            ),
            "errors": [err_msg],
        }


def content_node(state: SupervisorGraphState) -> Dict[str, Any]:
    """ContentAgent node: Crafts messaging, campaign hook, and content strategy."""
    decomposition = state.get("decomposition")
    user_request = state.get("user_request", "")
    research_output = state.get("research_output")
    
    subtask = next(
        (t for t in decomposition.subtasks if t.agent_type == "content"),
        None,
    ) if decomposition else None

    instructions = subtask.instructions if subtask else f"Develop content and messaging for: {user_request}"
    title = subtask.title if subtask else "Content Strategy"
    
    research_context = ""
    if research_output:
        research_context = (
            f"\nResearch Findings:\n"
            f"- Summary: {research_output.summary}\n"
            f"- Key Trends: {', '.join(research_output.market_trends)}\n"
            f"- Competitors: {', '.join(research_output.competitors)}\n"
            f"- Opportunities: {', '.join(research_output.opportunities)}\n"
        )

    logger.info("ContentAgent executing subtask: %s", title)
    prompt = (
        f"Topic / Request: {user_request}\n"
        f"Subtask Title: {title}\n"
        f"Instructions: {instructions}\n"
        f"{research_context}"
    )
    
    try:
        result = content_agent.run_sync(prompt)
        content_plan: ContentPlan = result.output
        logger.info("ContentAgent completed successfully.")
        return {"content_output": content_plan}
    except Exception as exc:
        err_msg = f"ContentAgent execution failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "content_output": ContentPlan(
                headline=f"Launch Campaign for {user_request}",
                core_messaging=f"Fallback positioning: {user_request}",
                target_channels=["Direct", "Social", "Email"],
                content_pieces=["Product Overview", "Launch Announcement"],
                call_to_action="Get Started Today",
            ),
            "errors": [err_msg],
        }


def financial_node(state: SupervisorGraphState) -> Dict[str, Any]:
    """FinancialAgent node: Models financial feasibility, costs, and monetization."""
    decomposition = state.get("decomposition")
    user_request = state.get("user_request", "")
    
    subtask = next(
        (t for t in decomposition.subtasks if t.agent_type == "financial"),
        None,
    ) if decomposition else None

    instructions = subtask.instructions if subtask else f"Evaluate financial viability for: {user_request}"
    title = subtask.title if subtask else "Financial Modeling"
    
    logger.info("FinancialAgent executing subtask: %s", title)
    prompt = f"Topic / Request: {user_request}\nSubtask Title: {title}\nInstructions: {instructions}"
    
    try:
        result = financial_agent.run_sync(prompt)
        financial_assessment: FinancialAssessment = result.output
        logger.info("FinancialAgent completed successfully.")
        return {"financial_output": financial_assessment}
    except Exception as exc:
        err_msg = f"FinancialAgent execution failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "financial_output": FinancialAssessment(
                estimated_setup_cost="$50,000 - $100,000 estimated initial spend",
                recurring_costs=["Infrastructure / Cloud", "Operations"],
                revenue_streams=["Subscription / Tiered SaaS"],
                break_even_timeline="12-18 months",
                financial_risks=[f"Calculation variance: {exc}"],
            ),
            "errors": [err_msg],
        }


def aggregate_node(state: SupervisorGraphState) -> Dict[str, Any]:
    """Supervisor node: Aggregates all specialist outputs into a final consolidated report."""
    user_request = state.get("user_request", "")
    decomposition = state.get("decomposition")
    research_output = state.get("research_output")
    content_output = state.get("content_output")
    financial_output = state.get("financial_output")
    
    logger.info("Supervisor Aggregator: Synthesizing final consolidated report...")
    
    prompt = (
        f"Original User Request:\n{user_request}\n\n"
        f"Decomposition Plan Summary:\n{decomposition.plan_summary if decomposition else 'N/A'}\n\n"
        f"Research Deliverable:\n{research_output.model_dump_json(indent=2) if research_output else 'No research output'}\n\n"
        f"Content Deliverable:\n{content_output.model_dump_json(indent=2) if content_output else 'No content output'}\n\n"
        f"Financial Deliverable:\n{financial_output.model_dump_json(indent=2) if financial_output else 'No financial output'}\n\n"
        f"Synthesize these findings into an executive, highly actionable ConsolidatedReport."
    )
    
    try:
        result = supervisor_aggregator_agent.run_sync(prompt)
        consolidated_report: ConsolidatedReport = result.output
        logger.info("Supervisor Aggregator synthesis complete.")
        return {"final_response": consolidated_report}
    except Exception as exc:
        err_msg = f"Supervisor Aggregator failed: {exc}"
        logger.error(err_msg, exc_info=True)
        return {
            "final_response": ConsolidatedReport(
                executive_summary=f"Consolidated strategy summary for: {user_request}",
                strategic_analysis="Automated aggregation encountered an error; fallback summary generated.",
                research_highlights=research_output.summary if research_output else "Research not available.",
                content_strategy_summary=content_output.core_messaging if content_output else "Content not available.",
                financial_outlook=financial_output.break_even_timeline if financial_output else "Financial outlook not available.",
                action_items=["Review domain findings", "Refine business model"],
            ),
            "errors": [err_msg],
        }


# Build LangGraph Workflow
workflow = StateGraph(SupervisorGraphState)

# Add Nodes
workflow.add_node("decompose", decompose_node)
workflow.add_node("research", research_node)
workflow.add_node("content", content_node)
workflow.add_node("financial", financial_node)
workflow.add_node("aggregate", aggregate_node)

# Add Edges
workflow.add_edge(START, "decompose")

# Parallel branch from decomposition
workflow.add_edge("decompose", "research")
workflow.add_edge("decompose", "financial")

# Both research and financial feed into content, which acts as the join/barrier
# point before aggregation. NOTE: LangGraph's Pregel scheduler fires a node as
# soon as any predecessor completes; if the paths from "decompose" to
# "aggregate" have uneven hop counts (e.g. financial->aggregate at 2 hops vs
# research->content->aggregate at 3 hops), "aggregate" fires once per
# arriving predecessor instead of once after all of them - causing the
# Supervisor aggregator LLM call to run twice per request. Routing both
# research and financial into content keeps all paths equal length.
workflow.add_edge("research", "content")
workflow.add_edge("financial", "content")

# Content converges into Supervisor Aggregator
workflow.add_edge("content", "aggregate")

# Aggregator finishes workflow
workflow.add_edge("aggregate", END)

# Compile LangGraph
supervisor_graph = workflow.compile()