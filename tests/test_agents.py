from agents.content import content_agent
from agents.financial import financial_agent
from agents.research import research_agent
from agents.supervisor import supervisor_aggregator_agent, supervisor_planner_agent
from state.schemas import (
    ConsolidatedReport,
    ContentPlan,
    FinancialAssessment,
    ResearchReport,
    TaskDecomposition,
)


def test_agent_configurations():
    # Verify output types
    assert supervisor_planner_agent.output_type == TaskDecomposition
    assert supervisor_aggregator_agent.output_type == ConsolidatedReport
    assert research_agent.output_type == ResearchReport
    assert content_agent.output_type == ContentPlan
    assert financial_agent.output_type == FinancialAssessment


def test_agent_prompts():
    assert "Supervisor" in supervisor_planner_agent._system_prompts[0]
    assert "Research" in research_agent._system_prompts[0]
    assert "Content" in content_agent._system_prompts[0]
    assert "Financial" in financial_agent._system_prompts[0]


def test_agent_tool_registration():
    # Research and financial agents should have registered function tools
    assert "perform_market_research" in research_agent._function_toolset.tools
    assert "calculate_financial_metrics" in financial_agent._function_toolset.tools
