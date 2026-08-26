from unittest.mock import MagicMock, patch
from graphs.supervisor_graph import (
    aggregate_node,
    content_node,
    decompose_node,
    financial_node,
    research_node,
    supervisor_graph,
)
from state.schemas import (
    ConsolidatedReport,
    ContentPlan,
    FinancialAssessment,
    ResearchReport,
    SubTask,
    TaskDecomposition,
)
from state.state import SupervisorGraphState


def test_parallel_node_failures_do_not_raise_invalid_update_error():
    """Regression test: research_node and financial_node run in parallel.
    If both fail in the same superstep and both try to write to the plain
    'errors' list, LangGraph raises InvalidUpdateError ("Can receive only
    one value per step") because it can't reconcile two concurrent writes
    to the same key without a reducer. The 'errors' field must stay
    Annotated with a reducer (e.g. operator.add) so simultaneous failures
    merge instead of crashing the whole run."""
    decomp = TaskDecomposition(
        plan_summary="p",
        subtasks=[
            SubTask(id="t1", agent_type="research", title="R", instructions="r"),
            SubTask(id="t2", agent_type="content", title="C", instructions="c"),
            SubTask(id="t3", agent_type="financial", title="F", instructions="f"),
        ],
    )

    with (
        patch("graphs.supervisor_graph.supervisor_planner_agent.run_sync") as mock_p,
        patch("graphs.supervisor_graph.research_agent.run_sync") as mock_r,
        patch("graphs.supervisor_graph.financial_agent.run_sync") as mock_f,
        patch("graphs.supervisor_graph.content_agent.run_sync") as mock_c,
        patch("graphs.supervisor_graph.supervisor_aggregator_agent.run_sync") as mock_a,
    ):
        mock_p.return_value = MagicMock(output=decomp)
        mock_r.side_effect = RuntimeError("boom research")
        mock_f.side_effect = RuntimeError("boom financial")
        mock_c.side_effect = RuntimeError("boom content")
        mock_a.side_effect = RuntimeError("boom aggregate")

        initial_state: SupervisorGraphState = {
            "user_request": "test",
            "decomposition": None,
            "research_output": None,
            "content_output": None,
            "financial_output": None,
            "final_response": None,
            "errors": [],
        }

        # This must not raise langgraph.errors.InvalidUpdateError.
        result = supervisor_graph.invoke(initial_state)

        assert len(result["errors"]) == 4
        assert any("ResearchAgent" in e for e in result["errors"])
        assert any("FinancialAgent" in e for e in result["errors"])
        assert any("ContentAgent" in e for e in result["errors"])
        assert any("Supervisor Aggregator" in e for e in result["errors"])


def test_supervisor_graph_compilation():
    assert supervisor_graph is not None
    # Check node presence
    nodes = supervisor_graph.nodes
    assert "decompose" in nodes
    assert "research" in nodes
    assert "content" in nodes
    assert "financial" in nodes
    assert "aggregate" in nodes


def test_decompose_node_mocked():
    mock_decomp = TaskDecomposition(
        plan_summary="Test Plan",
        subtasks=[
            SubTask(
                id="t1",
                agent_type="research",
                title="R Title",
                instructions="R Instr",
            ),
            SubTask(
                id="t2",
                agent_type="content",
                title="C Title",
                instructions="C Instr",
            ),
            SubTask(
                id="t3",
                agent_type="financial",
                title="F Title",
                instructions="F Instr",
            ),
        ],
    )
    with patch("graphs.supervisor_graph.supervisor_planner_agent.run_sync") as mock_run:
        mock_result = MagicMock()
        mock_result.output = mock_decomp
        mock_run.return_value = mock_result

        state: SupervisorGraphState = {
            "user_request": "Build a SaaS tool",
            "decomposition": None,
            "research_output": None,
            "content_output": None,
            "financial_output": None,
            "final_response": None,
            "errors": [],
        }

        output = decompose_node(state)
        assert "decomposition" in output
        assert len(output["decomposition"].subtasks) == 3


def test_specialist_and_aggregate_nodes_mocked():
    mock_decomp = TaskDecomposition(
        plan_summary="Test Plan",
        subtasks=[
            SubTask(id="t1", agent_type="research", title="R", instructions="Do research"),
            SubTask(id="t2", agent_type="content", title="C", instructions="Do content"),
            SubTask(id="t3", agent_type="financial", title="F", instructions="Do finance"),
        ],
    )
    mock_research = ResearchReport(
        summary="Research summary",
        market_trends=["Trend 1"],
        competitors=["Comp 1"],
        key_findings=["Finding 1"],
        opportunities=["Opp 1"],
    )
    mock_content = ContentPlan(
        headline="Awesome Headline",
        core_messaging="Value Prop",
        target_channels=["Web"],
        content_pieces=["Post"],
        call_to_action="Sign up",
    )
    mock_financial = FinancialAssessment(
        estimated_setup_cost="$10k",
        recurring_costs=["$1k/mo"],
        revenue_streams=["$10/mo"],
        break_even_timeline="6 mos",
        financial_risks=["Risk 1"],
    )
    mock_final = ConsolidatedReport(
        executive_summary="Exec summary",
        strategic_analysis="Strat analysis",
        research_highlights="Research highlights",
        content_strategy_summary="Content summary",
        financial_outlook="Financial outlook",
        action_items=["Step 1"],
    )

    state: SupervisorGraphState = {
        "user_request": "Build a SaaS tool",
        "decomposition": mock_decomp,
        "research_output": None,
        "content_output": None,
        "financial_output": None,
        "final_response": None,
        "errors": [],
    }

    with patch("graphs.supervisor_graph.research_agent.run_sync") as mock_r:
        mock_r.return_value = MagicMock(output=mock_research)
        r_out = research_node(state)
        assert r_out["research_output"].summary == "Research summary"
        state["research_output"] = r_out["research_output"]

    with patch("graphs.supervisor_graph.content_agent.run_sync") as mock_c:
        mock_c.return_value = MagicMock(output=mock_content)
        c_out = content_node(state)
        assert c_out["content_output"].headline == "Awesome Headline"
        state["content_output"] = c_out["content_output"]

    with patch("graphs.supervisor_graph.financial_agent.run_sync") as mock_f:
        mock_f.return_value = MagicMock(output=mock_financial)
        f_out = financial_node(state)
        assert f_out["financial_output"].estimated_setup_cost == "$10k"
        state["financial_output"] = f_out["financial_output"]

    with patch("graphs.supervisor_graph.supervisor_aggregator_agent.run_sync") as mock_a:
        mock_a.return_value = MagicMock(output=mock_final)
        a_out = aggregate_node(state)
        assert a_out["final_response"].executive_summary == "Exec summary"


def test_end_to_end_graph_execution_mocked():
    mock_decomp = TaskDecomposition(
        plan_summary="E2E Plan",
        subtasks=[
            SubTask(id="t1", agent_type="research", title="R", instructions="Do R"),
            SubTask(id="t2", agent_type="content", title="C", instructions="Do C"),
            SubTask(id="t3", agent_type="financial", title="F", instructions="Do F"),
        ],
    )
    mock_research = ResearchReport(
        summary="E2E Research",
        market_trends=["T1"],
        competitors=["C1"],
        key_findings=["K1"],
        opportunities=["O1"],
    )
    mock_content = ContentPlan(
        headline="E2E Headline",
        core_messaging="E2E Messaging",
        target_channels=["Ch1"],
        content_pieces=["P1"],
        call_to_action="CTA",
    )
    mock_financial = FinancialAssessment(
        estimated_setup_cost="$20k",
        recurring_costs=["$2k"],
        revenue_streams=["$20"],
        break_even_timeline="12 mos",
        financial_risks=["None"],
    )
    mock_final = ConsolidatedReport(
        executive_summary="E2E Exec",
        strategic_analysis="E2E Strat",
        research_highlights="E2E Res",
        content_strategy_summary="E2E Cont",
        financial_outlook="E2E Fin",
        action_items=["Item 1"],
    )

    with (
        patch("graphs.supervisor_graph.supervisor_planner_agent.run_sync") as mock_p,
        patch("graphs.supervisor_graph.research_agent.run_sync") as mock_r,
        patch("graphs.supervisor_graph.content_agent.run_sync") as mock_c,
        patch("graphs.supervisor_graph.financial_agent.run_sync") as mock_f,
        patch("graphs.supervisor_graph.supervisor_aggregator_agent.run_sync") as mock_a,
    ):
        mock_p.return_value = MagicMock(output=mock_decomp)
        mock_r.return_value = MagicMock(output=mock_research)
        mock_c.return_value = MagicMock(output=mock_content)
        mock_f.return_value = MagicMock(output=mock_financial)
        mock_a.return_value = MagicMock(output=mock_final)

        initial_state: SupervisorGraphState = {
            "user_request": "Launch AI Developer Assistant",
            "decomposition": None,
            "research_output": None,
            "content_output": None,
            "financial_output": None,
            "final_response": None,
            "errors": [],
        }

        result = supervisor_graph.invoke(initial_state)

        assert result["decomposition"] is not None
        assert result["research_output"].summary == "E2E Research"
        assert result["content_output"].headline == "E2E Headline"
        assert result["financial_output"].estimated_setup_cost == "$20k"
        assert result["final_response"].executive_summary == "E2E Exec"
        assert len(result["final_response"].action_items) == 1

        # Regression test: LangGraph's Pregel scheduler fires a node as soon
        # as any predecessor completes. If paths into "aggregate" have
        # uneven hop counts, it fires once per arriving predecessor instead
        # of once after all of them - silently doubling the (costly) final
        # LLM call. Assert every node, especially aggregate, runs exactly
        # once per graph invocation.
        assert mock_p.call_count == 1, "planner should run exactly once"
        assert mock_r.call_count == 1, "research agent should run exactly once"
        assert mock_c.call_count == 1, "content agent should run exactly once"
        assert mock_f.call_count == 1, "financial agent should run exactly once"
        assert mock_a.call_count == 1, "aggregator should run exactly once (fan-in bug regression)"