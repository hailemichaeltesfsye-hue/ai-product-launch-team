from agents.ceo import CeoDecomposition, ceo_aggregator_agent, ceo_planner_agent
from agents.cost import cost_agent
from agents.finance_manager import (
    finance_manager_aggregator_agent,
    finance_manager_planner_agent,
)
from agents.marketing_manager import (
    marketing_manager_aggregator_agent,
    marketing_manager_planner_agent,
)
from agents.pricing import pricing_agent
from state.schemas import (
    CostAssessment,
    ExecutiveReport,
    FinanceReport,
    MarketingReport,
    PricingStrategy,
    TaskDecomposition,
)


def test_ceo_agent_output_types():
    assert ceo_planner_agent.output_type is CeoDecomposition
    assert ceo_aggregator_agent.output_type is ExecutiveReport


def test_marketing_manager_output_types():
    assert marketing_manager_planner_agent.output_type is TaskDecomposition
    assert marketing_manager_aggregator_agent.output_type is MarketingReport


def test_finance_manager_output_types():
    assert finance_manager_planner_agent.output_type is TaskDecomposition
    assert finance_manager_aggregator_agent.output_type is FinanceReport


def test_cost_agent_output_type_and_tools():
    assert cost_agent.output_type is CostAssessment
    tool_names = set(cost_agent._function_toolset.tools.keys())
    assert "calculate_financial_metrics" in tool_names


def test_pricing_agent_output_type():
    assert pricing_agent.output_type is PricingStrategy


def test_all_hierarchical_agents_have_retry_budget():
    agents = [
        ceo_planner_agent,
        ceo_aggregator_agent,
        marketing_manager_planner_agent,
        marketing_manager_aggregator_agent,
        finance_manager_planner_agent,
        finance_manager_aggregator_agent,
        cost_agent,
        pricing_agent,
    ]
    for agent in agents:
        assert agent._max_output_retries >= 3, f"{agent} should have a retry budget >= 3"