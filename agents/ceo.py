from pydantic import BaseModel, Field
from pydantic_ai import Agent
from agents.model import get_groq_model
from state.schemas import ExecutiveReport

# Model instance
model = get_groq_model()


class CeoDecomposition(BaseModel):
    """CEO's decomposition of the user's request into directives for each manager."""

    plan_summary: str = Field(
        description="Strategic summary of the overall plan and delegation rationale"
    )
    marketing_directive: str = Field(
        description="Detailed directive/instructions for the Marketing Manager"
    )
    finance_directive: str = Field(
        description="Detailed directive/instructions for the Finance Manager"
    )


# 1. CEO Planner - decomposes the user's request into directives for the
#    Marketing Manager and Finance Manager.
ceo_planner_agent = Agent(
    model=model,
    output_type=CeoDecomposition,
    retries=3,
    system_prompt=(
        "You are the CEO of a company, responsible for turning a business/product request into "
        "clear strategic directives for your two direct reports:\n\n"
        "1. Marketing Manager: Owns market research, positioning, messaging, and go-to-market channels.\n"
        "2. Finance Manager: Owns cost structure, break-even analysis, pricing strategy, and revenue model.\n\n"
        "Write a concise plan_summary describing your overall strategy, then write a detailed "
        "marketing_directive and a detailed finance_directive - each specific enough for that "
        "manager to independently decompose further for their own team.\n\n"
        "IMPORTANT: Never ask for clarification and never respond with plain conversational text. "
        "Even if the request is vague or generic, make reasonable, clearly-labeled assumptions and proceed."
    ),
)

# 2. CEO Aggregator - synthesizes MarketingReport + FinanceReport into the
#    final ExecutiveReport.
ceo_aggregator_agent = Agent(
    model=model,
    output_type=ExecutiveReport,
    retries=3,
    system_prompt=(
        "You are the CEO, synthesizing reports from your two managers (Marketing Manager and "
        "Finance Manager) into a single authoritative ExecutiveReport for the board.\n\n"
        "You will be given the original user request, the Marketing Manager's MarketingReport, "
        "and the Finance Manager's FinanceReport. Connect strategic dots across marketing and "
        "finance, eliminate redundancy, and produce a cohesive executive_summary, "
        "strategic_analysis, marketing_highlights, finance_highlights, and concrete action_items.\n\n"
        "IMPORTANT: Never ask for clarification and never respond with plain conversational text. "
        "Always return a fully populated, structured ExecutiveReport as your entire response, even "
        "if one of the manager reports is missing."
    ),
)