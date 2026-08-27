from unittest.mock import MagicMock, patch

from agents.ceo import CeoDecomposition
from graphs.ceo_graph import ceo_graph
from graphs.finance_subgraph import finance_subgraph
from graphs.marketing_subgraph import marketing_subgraph
from state.schemas import (
    ContentPlan,
    CostAssessment,
    ExecutiveReport,
    FinanceReport,
    MarketingReport,
    PricingStrategy,
    ResearchReport,
    SubTask,
    TaskDecomposition,
)
from state.state import HierarchicalState


def _initial_state(user_request: str = "Launch an AI-powered tool.") -> HierarchicalState:
    return {
        "user_request": user_request,
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


def test_marketing_subgraph_compiles_with_expected_nodes():
    nodes = marketing_subgraph.get_graph().nodes
    assert "decompose" in nodes
    assert "research" in nodes
    assert "content" in nodes
    assert "aggregate" in nodes


def test_finance_subgraph_compiles_with_expected_nodes():
    nodes = finance_subgraph.get_graph().nodes
    assert "decompose" in nodes
    assert "cost" in nodes
    assert "pricing" in nodes
    assert "aggregate" in nodes


def test_ceo_graph_compiles_with_expected_nodes():
    nodes = ceo_graph.get_graph().nodes
    assert "decompose" in nodes
    assert "marketing" in nodes
    assert "finance" in nodes
    assert "aggregate" in nodes


def test_finance_subgraph_parallel_fanin_fires_aggregate_once():
    """Regression test: cost_node and pricing_node run in parallel (both 1
    hop from finance_decompose). Assert finance_aggregate_node - and every
    other node - fires exactly once per invocation."""
    decomp = TaskDecomposition(
        plan_summary="p",
        subtasks=[
            SubTask(id="t1", agent_type="cost", title="C", instructions="c"),
            SubTask(id="t2", agent_type="pricing", title="P", instructions="p"),
        ],
    )
    cost = CostAssessment(estimated_setup_cost="1", break_even_timeline="1")
    pricing = PricingStrategy(pricing_model="m")
    finrep = FinanceReport(summary="s", cost_overview="c", pricing_overview="p")

    with (
        patch("graphs.finance_subgraph.finance_manager_planner_agent.run_sync") as mock_p,
        patch("graphs.finance_subgraph.cost_agent.run_sync") as mock_c,
        patch("graphs.finance_subgraph.pricing_agent.run_sync") as mock_pr,
        patch("graphs.finance_subgraph.finance_manager_aggregator_agent.run_sync") as mock_a,
    ):
        mock_p.return_value = MagicMock(output=decomp)
        mock_c.return_value = MagicMock(output=cost)
        mock_pr.return_value = MagicMock(output=pricing)
        mock_a.return_value = MagicMock(output=finrep)

        state = _initial_state()
        state["finance_directive"] = "test finance directive"
        result = finance_subgraph.invoke(state)

        assert mock_p.call_count == 1
        assert mock_c.call_count == 1
        assert mock_pr.call_count == 1
        assert mock_a.call_count == 1, "finance_aggregate_node must fire exactly once (equal-depth fan-in)"
        assert result["finance_report"] == finrep
        assert result["errors"] == []


def test_ceo_graph_full_happy_path_fires_every_agent_once():
    """Full end-to-end mocked run through the entire 3-level hierarchy.
    Every one of the 10 underlying agent calls (CEO planner/aggregator,
    2 manager planners, 2 manager aggregators, 4 specialists) must fire
    exactly once, and data must flow correctly from specialists up through
    managers to the final ExecutiveReport."""
    ceo_decomp = CeoDecomposition(plan_summary="p", marketing_directive="mkt", finance_directive="fin")
    mkt_decomp = TaskDecomposition(
        plan_summary="p",
        subtasks=[
            SubTask(id="t1", agent_type="research", title="R", instructions="r"),
            SubTask(id="t2", agent_type="content", title="C", instructions="c"),
        ],
    )
    fin_decomp = TaskDecomposition(
        plan_summary="p",
        subtasks=[
            SubTask(id="t1", agent_type="cost", title="Co", instructions="co"),
            SubTask(id="t2", agent_type="pricing", title="P", instructions="p"),
        ],
    )
    research = ResearchReport(summary="r")
    content = ContentPlan(headline="h", core_messaging="m", call_to_action="cta")
    mkt_report = MarketingReport(summary="s", market_positioning="pos", messaging_summary="ms")
    cost = CostAssessment(estimated_setup_cost="1", break_even_timeline="1")
    pricing = PricingStrategy(pricing_model="m")
    fin_report = FinanceReport(summary="s", cost_overview="c", pricing_overview="p")
    exec_report = ExecutiveReport(
        executive_summary="e", strategic_analysis="a", marketing_highlights="m", finance_highlights="f"
    )

    with (
        patch("graphs.ceo_graph.ceo_planner_agent.run_sync") as m_ceo_p,
        patch("graphs.marketing_subgraph.marketing_manager_planner_agent.run_sync") as m_mkt_p,
        patch("graphs.marketing_subgraph.research_agent.run_sync") as m_r,
        patch("graphs.marketing_subgraph.content_agent.run_sync") as m_c,
        patch("graphs.marketing_subgraph.marketing_manager_aggregator_agent.run_sync") as m_mkt_a,
        patch("graphs.finance_subgraph.finance_manager_planner_agent.run_sync") as m_fin_p,
        patch("graphs.finance_subgraph.cost_agent.run_sync") as m_co,
        patch("graphs.finance_subgraph.pricing_agent.run_sync") as m_pr,
        patch("graphs.finance_subgraph.finance_manager_aggregator_agent.run_sync") as m_fin_a,
        patch("graphs.ceo_graph.ceo_aggregator_agent.run_sync") as m_ceo_a,
    ):
        m_ceo_p.return_value = MagicMock(output=ceo_decomp)
        m_mkt_p.return_value = MagicMock(output=mkt_decomp)
        m_r.return_value = MagicMock(output=research)
        m_c.return_value = MagicMock(output=content)
        m_mkt_a.return_value = MagicMock(output=mkt_report)
        m_fin_p.return_value = MagicMock(output=fin_decomp)
        m_co.return_value = MagicMock(output=cost)
        m_pr.return_value = MagicMock(output=pricing)
        m_fin_a.return_value = MagicMock(output=fin_report)
        m_ceo_a.return_value = MagicMock(output=exec_report)

        result = ceo_graph.invoke(_initial_state())

        for name, mock in [
            ("ceo_planner", m_ceo_p), ("mkt_planner", m_mkt_p), ("research", m_r),
            ("content", m_c), ("mkt_aggregator", m_mkt_a), ("fin_planner", m_fin_p),
            ("cost", m_co), ("pricing", m_pr), ("fin_aggregator", m_fin_a),
            ("ceo_aggregator", m_ceo_a),
        ]:
            assert mock.call_count == 1, f"{name} should fire exactly once"

        assert result["research_output"] == research
        assert result["content_output"] == content
        assert result["marketing_report"] == mkt_report
        assert result["cost_output"] == cost
        assert result["pricing_output"] == pricing
        assert result["finance_report"] == fin_report
        assert result["final_response"] == exec_report
        assert result["errors"] == []


def test_ceo_graph_errors_are_not_double_counted_across_subgraphs():
    """Regression test: marketing_subgraph_node and finance_subgraph_node
    each invoke their compiled subgraph on a *copy* of the parent state.
    If "errors" isn't reset to [] before invoking, each subgraph's inherited
    copy of the parent's already-accumulated errors gets returned again and
    re-added by the parent's operator.add reducer - silently multiplying
    every pre-existing error by the number of parallel branches. Simulate
    every agent in the hierarchy failing and assert each of the 10 distinct
    error messages appears exactly once, not duplicated."""
    with (
        patch("graphs.ceo_graph.ceo_planner_agent.run_sync", side_effect=RuntimeError("ceo planner boom")),
        patch(
            "graphs.marketing_subgraph.marketing_manager_planner_agent.run_sync",
            side_effect=RuntimeError("mkt planner boom"),
        ),
        patch("graphs.marketing_subgraph.research_agent.run_sync", side_effect=RuntimeError("research boom")),
        patch("graphs.marketing_subgraph.content_agent.run_sync", side_effect=RuntimeError("content boom")),
        patch(
            "graphs.marketing_subgraph.marketing_manager_aggregator_agent.run_sync",
            side_effect=RuntimeError("mkt agg boom"),
        ),
        patch(
            "graphs.finance_subgraph.finance_manager_planner_agent.run_sync",
            side_effect=RuntimeError("fin planner boom"),
        ),
        patch("graphs.finance_subgraph.cost_agent.run_sync", side_effect=RuntimeError("cost boom")),
        patch("graphs.finance_subgraph.pricing_agent.run_sync", side_effect=RuntimeError("pricing boom")),
        patch(
            "graphs.finance_subgraph.finance_manager_aggregator_agent.run_sync",
            side_effect=RuntimeError("fin agg boom"),
        ),
        patch("graphs.ceo_graph.ceo_aggregator_agent.run_sync", side_effect=RuntimeError("ceo agg boom")),
    ):
        result = ceo_graph.invoke(_initial_state())

        assert len(result["errors"]) == 10, (
            f"expected exactly 10 distinct errors (one per failing agent), got "
            f"{len(result['errors'])}: {result['errors']}"
        )
        assert len(set(result["errors"])) == 10, "no error message should be duplicated"
        assert result["final_response"] is not None, "CEO aggregate fallback should still populate a response"