import operator
from typing import List, Optional
from typing_extensions import Annotated, TypedDict
from state.schemas import (
    ConsolidatedReport,
    ContentPlan,
    CostAssessment,
    ExecutiveReport,
    AgentHandoff,
    FinanceReport,
    FinancialAssessment,
    MarketingReport,
    PricingStrategy,
    ResearchReport,
    TaskDecomposition,
)


def latest_agent(current: Optional[str], incoming: Optional[str]) -> Optional[str]:
    """Resolve concurrent progress markers while preserving the newest update."""
    return incoming or current


class SupervisorGraphState(TypedDict):
    """LangGraph workflow state structure for the Supervisor Multi-Agent System."""

    user_request: str
    decomposition: Optional[TaskDecomposition]
    research_output: Optional[ResearchReport]
    content_output: Optional[ContentPlan]
    financial_output: Optional[FinancialAssessment]
    final_response: Optional[ConsolidatedReport]
    # Annotated with operator.add so that when parallel nodes (e.g. research
    # and financial) both write to "errors" in the same superstep, LangGraph
    # concatenates the lists instead of raising InvalidUpdateError ("Can
    # receive only one value per step").
    errors: Annotated[List[str], operator.add]


class HierarchicalState(TypedDict):
    """Shared LangGraph state for the hierarchical CEO -> Manager -> Specialist
    architecture. A single schema is used across the top-level CEO graph and
    both the Marketing and Finance manager subgraphs, so state flows through
    the whole hierarchy without any translation between graph levels. Each
    node reads/writes only the keys relevant to its own level."""

    user_request: str

    # Explicit handoff tracking. The reducer is required because the CEO's
    # marketing and finance branches can append handoffs concurrently.
    current_agent: Annotated[Optional[str], latest_agent]
    handoff_history: Annotated[List[AgentHandoff], operator.add]

    # CEO -> Managers
    marketing_directive: Optional[str]
    finance_directive: Optional[str]

    # Internal bookkeeping: each manager's own decomposition of its directive
    # into subtasks for its specialist agents (mirrors the flat system's
    # top-level "decomposition" field, but scoped per manager).
    marketing_decomposition: Optional[TaskDecomposition]
    finance_decomposition: Optional[TaskDecomposition]

    # Marketing Manager -> specialists, and their outputs
    research_output: Optional[ResearchReport]
    content_output: Optional[ContentPlan]
    marketing_report: Optional[MarketingReport]

    # Finance Manager -> specialists, and their outputs
    cost_output: Optional[CostAssessment]
    pricing_output: Optional[PricingStrategy]
    finance_report: Optional[FinanceReport]

    # CEO's final synthesis
    final_response: Optional[ExecutiveReport]

    # Reducer required: multiple nodes across different branches of the
    # hierarchy (research/content, cost/pricing, marketing/finance subgraphs)
    # can all fail in the same superstep and need to write errors concurrently.
    errors: Annotated[List[str], operator.add]