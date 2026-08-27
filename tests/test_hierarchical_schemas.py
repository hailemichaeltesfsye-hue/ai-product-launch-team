from state.schemas import (
    CostAssessment,
    ExecutiveReport,
    FinanceReport,
    MarketingReport,
    PricingStrategy,
    SubTask,
)
from state.state import HierarchicalState


def test_subtask_supports_hierarchical_agent_types():
    SubTask(id="t1", agent_type="cost", title="Cost", instructions="do cost")
    SubTask(id="t2", agent_type="pricing", title="Pricing", instructions="do pricing")


def test_cost_assessment_schema():
    ca = CostAssessment(
        estimated_setup_cost="$50,000",
        recurring_costs=["$5k/mo"],
        break_even_timeline="8 months",
        cost_risks=["High CAC"],
    )
    assert ca.estimated_setup_cost == "$50,000"


def test_pricing_strategy_schema():
    ps = PricingStrategy(
        pricing_model="Tiered SaaS",
        pricing_tiers=["Basic $29/mo", "Pro $79/mo"],
        revenue_streams=["Subscriptions"],
        pricing_risks=["Price sensitivity"],
    )
    assert len(ps.pricing_tiers) == 2


def test_marketing_report_schema():
    mr = MarketingReport(
        summary="s",
        market_positioning="pos",
        key_research_insights=["insight 1"],
        messaging_summary="ms",
        recommended_channels=["LinkedIn"],
    )
    assert mr.summary == "s"


def test_finance_report_schema():
    fr = FinanceReport(
        summary="s",
        cost_overview="co",
        pricing_overview="po",
        financial_risks=["risk1"],
    )
    assert fr.cost_overview == "co"


def test_executive_report_schema():
    er = ExecutiveReport(
        executive_summary="e",
        strategic_analysis="a",
        marketing_highlights="m",
        finance_highlights="f",
        action_items=["item1"],
    )
    assert len(er.action_items) == 1


def test_hierarchical_state_shape():
    state: HierarchicalState = {
        "user_request": "Launch a tool",
        "marketing_directive": None,
        "finance_directive": None,
        "marketing_decomposition": None,
        "finance_decomposition": None,
        "research_output": None,
        "content_output": None,
        "marketing_report": None,
        "cost_output": None,
        "pricing_output": None,
        "finance_report": None,
        "final_response": None,
        "errors": [],
    }
    assert state["user_request"] == "Launch a tool"
    assert state["errors"] == []