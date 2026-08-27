import logging
from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from agents.content import content_agent
from agents.finance import finance_agent
from agents.research import research_agent
from state.p2p_state import P2PState
from state.schemas import AgentMessage, ContentPlan, FinancialAssessment, LaunchSynthesis, ResearchReport

logger = logging.getLogger(__name__)


def research_peer(state: P2PState) -> Dict[str, Any]:
    request = state.get("user_request", "")
    prompt = (
        f"Launch brief: {request}\n\n"
        "You are working peer-to-peer. Analyze market trends, competitors, findings, "
        "and opportunities. Flag any financial assumptions FinanceAgent should clarify."
    )
    try:
        result = research_agent.run_sync(prompt)
        report: ResearchReport = result.output
        return {
            "research_output": report,
            "messages": [
                AgentMessage(sender="research", recipient="finance", message_type="request", content="Please validate the cost and willingness-to-pay assumptions behind these market opportunities."),
                AgentMessage(sender="research", recipient="content", message_type="handoff", content=f"Research is ready: {report.summary}"),
            ],
        }
    except Exception as exc:
        error = f"ResearchAgent failed: {exc}"
        return {"research_output": None, "errors": [error]}


def finance_peer(state: P2PState) -> Dict[str, Any]:
    request = state.get("user_request", "")
    research = state.get("research_output")
    prompt = (
        f"Launch brief: {request}\n\n"
        f"ResearchAgent request and findings:\n{research.model_dump_json(indent=2) if research else 'Unavailable'}\n\n"
        "Respond directly to ResearchAgent's clarification request. Build the complete cost and pricing plan."
    )
    try:
        result = finance_agent.run_sync(prompt)
        assessment: FinancialAssessment = result.output
        return {
            "finance_output": assessment,
            "messages": [
                AgentMessage(sender="finance", recipient="research", message_type="response", content=f"Finance assumptions validated. Break-even: {assessment.break_even_timeline}"),
                AgentMessage(sender="finance", recipient="content", message_type="insight", content=f"Pricing signal: {', '.join(assessment.revenue_streams)}"),
            ],
        }
    except Exception as exc:
        return {"finance_output": None, "errors": [f"FinanceAgent failed: {exc}"]}


def content_peer(state: P2PState) -> Dict[str, Any]:
    request = state.get("user_request", "")
    research = state.get("research_output")
    finance = state.get("finance_output")
    prompt = (
        f"Launch brief: {request}\n\n"
        f"ResearchAgent data:\n{research.model_dump_json(indent=2) if research else 'Unavailable'}\n\n"
        f"FinanceAgent data:\n{finance.model_dump_json(indent=2) if finance else 'Unavailable'}\n\n"
        "Request the research data you need implicitly through this shared mailbox, then create the content plan."
    )
    try:
        result = content_agent.run_sync(prompt)
        plan: ContentPlan = result.output
        return {
            "content_output": plan,
            "messages": [AgentMessage(sender="content", recipient="research", message_type="request", content="I used your research data to shape the launch narrative and channel mix.")],
        }
    except Exception as exc:
        return {"content_output": None, "errors": [f"ContentAgent failed: {exc}"]}


def synthesis_node(state: P2PState) -> Dict[str, Any]:
    research = state.get("research_output")
    finance = state.get("finance_output")
    content = state.get("content_output")
    if not all((research, finance, content)):
        return {"launch_synthesis": None, "errors": ["Launch synthesis skipped because a peer did not return a deliverable."]}
    return {
        "launch_synthesis": LaunchSynthesis(
            executive_summary=content.core_messaging,
            market_thesis=research.summary,
            messaging_direction=f"{content.headline} | CTA: {content.call_to_action}",
            financial_direction=f"{finance.estimated_setup_cost}; {finance.break_even_timeline}",
            action_items=[*research.opportunities[:2], *content.content_pieces[:2]],
        )
    }


workflow = StateGraph(P2PState)
workflow.add_node("research", research_peer)
workflow.add_node("finance", finance_peer)
workflow.add_node("content", content_peer)
workflow.add_node("synthesis", synthesis_node)
workflow.add_edge(START, "research")
workflow.add_edge("research", "finance")
workflow.add_edge("finance", "content")
workflow.add_edge("content", "synthesis")
workflow.add_edge("synthesis", END)
p2p_graph = workflow.compile()