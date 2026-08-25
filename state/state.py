from typing import List, Optional
from typing_extensions import TypedDict
from state.schemas import (
    FinalLaunchArtifact,
    MarketingPlan,
    ProductBrief,
    TechnicalArchitecture,
)


class LaunchGraphState(TypedDict):
    """LangGraph workflow state structure."""

    product_idea: str
    product_brief: Optional[ProductBrief]
    tech_specs: Optional[TechnicalArchitecture]
    marketing_plan: Optional[MarketingPlan]
    final_package: Optional[FinalLaunchArtifact]
    errors: List[str]
