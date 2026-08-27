import operator
from typing import List, Optional
from typing_extensions import Annotated, TypedDict

from state.schemas import AgentMessage, ContentPlan, FinancialAssessment, LaunchSynthesis, ResearchReport


class P2PState(TypedDict):
    """Shared state and mailbox for the decentralized peer network."""

    user_request: str
    research_output: Optional[ResearchReport]
    finance_output: Optional[FinancialAssessment]
    content_output: Optional[ContentPlan]
    launch_synthesis: Optional[LaunchSynthesis]
    messages: Annotated[List[AgentMessage], operator.add]
    errors: Annotated[List[str], operator.add]