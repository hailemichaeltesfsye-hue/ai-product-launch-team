import operator
from typing import List, Optional
from typing_extensions import Annotated, TypedDict
from state.schemas import (
    ConsolidatedReport,
    ContentPlan,
    FinancialAssessment,
    ResearchReport,
    TaskDecomposition,
)


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