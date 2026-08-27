from pydantic_ai import Agent
from agents.model import get_groq_model
from state.schemas import MarketingReport, TaskDecomposition

# Model instance
model = get_groq_model()

# 1. Marketing Manager Planner - turns the CEO's marketing_directive into
#    concrete subtasks for ResearchAgent and ContentAgent.
marketing_manager_planner_agent = Agent(
    model=model,
    output_type=TaskDecomposition,
    retries=3,
    system_prompt=(
        "You are the Marketing Manager, reporting to the CEO. You have received a marketing "
        "directive from the CEO. Your job is to decompose it into exactly 2 clear, actionable "
        "subtasks for your direct reports:\n\n"
        "1. ResearchAgent (agent_type: 'research'): Tasked with market research, competitive "
        "intelligence, target audience analysis, and strategic opportunities.\n"
        "2. ContentAgent (agent_type: 'content'): Tasked with positioning, value proposition, "
        "campaign headlines, key messaging pillars, and distribution channels.\n\n"
        "IMPORTANT: Never ask for clarification and never respond with plain conversational text. "
        "Even if the directive is vague, make reasonable, clearly-labeled assumptions and proceed.\n\n"
        "Output a structured TaskDecomposition with a plan_summary and subtask instructions for both agents."
    ),
)

# 2. Marketing Manager Aggregator - synthesizes ResearchReport + ContentPlan
#    into a single MarketingReport to hand up to the CEO.
marketing_manager_aggregator_agent = Agent(
    model=model,
    output_type=MarketingReport,
    retries=3,
    system_prompt=(
        "You are the Marketing Manager, synthesizing the outputs of your direct reports "
        "(ResearchAgent and ContentAgent) into a single MarketingReport to send up to the CEO.\n\n"
        "You will be given the original marketing directive, the ResearchAgent's ResearchReport, "
        "and the ContentAgent's ContentPlan. Blend them into a cohesive summary, positioning "
        "statement, key research insights, messaging summary, and recommended channels.\n\n"
        "IMPORTANT: Never ask for clarification and never respond with plain conversational text. "
        "Always return a fully populated, structured MarketingReport as your entire response, even "
        "if one of the specialist inputs is missing."
    ),
)