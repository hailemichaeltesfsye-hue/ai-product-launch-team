import pytest
from state.schemas import (
    ConsolidatedReport,
    ContentPlan,
    FinancialAssessment,
    ResearchReport,
    SubTask,
    TaskDecomposition,
)
from state.state import SupervisorGraphState


def test_subtask_schema():
    subtask = SubTask(
        id="task_1",
        agent_type="research",
        title="Market Analysis",
        instructions="Analyze the market for AI tools",
    )
    assert subtask.id == "task_1"
    assert subtask.agent_type == "research"
    assert subtask.title == "Market Analysis"


def test_task_decomposition_schema():
    decomp = TaskDecomposition(
        plan_summary="Breakdown of launch strategy",
        subtasks=[
            SubTask(
                id="t1",
                agent_type="research",
                title="Research Task",
                instructions="Research competitors",
            ),
            SubTask(
                id="t2",
                agent_type="content",
                title="Content Task",
                instructions="Write copy",
            ),
            SubTask(
                id="t3",
                agent_type="financial",
                title="Financial Task",
                instructions="Model pricing",
            ),
        ],
    )
    assert len(decomp.subtasks) == 3
    assert decomp.subtasks[0].agent_type == "research"


def test_research_report_schema():
    report = ResearchReport(
        summary="Strong demand in enterprise segment.",
        market_trends=["AI automation", "Cloud native"],
        competitors=["Competitor Alpha", "Competitor Beta"],
        key_findings=["70% of teams require integration"],
        opportunities=["Underserved mid-market segment"],
    )
    assert report.summary.startswith("Strong demand")
    assert len(report.competitors) == 2


def test_content_plan_schema():
    plan = ContentPlan(
        headline="Revolutionize Developer Productivity",
        core_messaging="Streamline workflows with autonomous AI assistance.",
        target_channels=["Hacker News", "Product Hunt", "LinkedIn"],
        content_pieces=["Blog Post", "Quickstart Video", "Case Study"],
        call_to_action="Start your free trial today",
    )
    assert "Developer Productivity" in plan.headline
    assert len(plan.target_channels) == 3


def test_financial_assessment_schema():
    financial = FinancialAssessment(
        estimated_setup_cost="$50,000",
        recurring_costs=["$5,000/month infrastructure", "$10,000/month operations"],
        revenue_streams=["$29/user/month Pro plan", "$99/user/month Enterprise"],
        break_even_timeline="8 months",
        financial_risks=["High initial customer acquisition cost"],
    )
    assert financial.estimated_setup_cost == "$50,000"
    assert len(financial.revenue_streams) == 2


def test_consolidated_report_schema():
    consolidated = ConsolidatedReport(
        executive_summary="Launch approved for Q3 with strong feasibility.",
        strategic_analysis="Market positioning leverages low-cost entry and high velocity.",
        research_highlights="Growing at 25% CAGR.",
        content_strategy_summary="Multi-channel content blitz across tech communities.",
        financial_outlook="Profitable within 8 months based on $29/mo tier.",
        action_items=["Finalize MVP", "Launch landing page", "Onboard beta users"],
    )
    assert len(consolidated.action_items) == 3


def test_supervisor_graph_state():
    state: SupervisorGraphState = {
        "user_request": "Launch AI tool",
        "decomposition": None,
        "research_output": None,
        "content_output": None,
        "financial_output": None,
        "final_response": None,
        "errors": [],
    }
    assert state["user_request"] == "Launch AI tool"
    assert state["errors"] == []
