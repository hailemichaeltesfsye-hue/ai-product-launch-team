from pydantic_ai import Agent
from agents.model import get_groq_model
from state.schemas import FinanceReport, TaskDecomposition

# Model instance
model = get_groq_model()

# 1. Finance Manager Planner - turns the CEO's finance_directive into
#    concrete subtasks for CostAgent and PricingAgent.
finance_manager_planner_agent = Agent(
    model=model,
    output_type=TaskDecomposition,
    retries=3,
    system_prompt=(
        "You are the Finance Manager, reporting to the CEO. You have received a finance "
        "directive from the CEO. Your job is to decompose it into exactly 2 clear, actionable "
        "subtasks for your direct reports:\n\n"
        "1. CostAgent (agent_type: 'cost'): Tasked with setup costs, recurring operating "
        "expenses, and break-even timeline analysis.\n"
        "2. PricingAgent (agent_type: 'pricing'): Tasked with pricing model, pricing tiers, "
        "and revenue stream strategy.\n\n"
        "IMPORTANT: Never ask for clarification and never respond with plain conversational text. "
        "Even if the directive is vague, make reasonable, clearly-labeled assumptions and proceed.\n\n"
        "Output a structured TaskDecomposition with a plan_summary and subtask instructions for both agents."
    ),
)

# 2. Finance Manager Aggregator - synthesizes CostAssessment + PricingStrategy
#    into a single FinanceReport to hand up to the CEO.
finance_manager_aggregator_agent = Agent(
    model=model,
    output_type=FinanceReport,
    retries=3,
    system_prompt=(
        "You are the Finance Manager, synthesizing the outputs of your direct reports "
        "(CostAgent and PricingAgent) into a single FinanceReport to send up to the CEO.\n\n"
        "You will be given the original finance directive, the CostAgent's CostAssessment, "
        "and the PricingAgent's PricingStrategy. Blend them into a cohesive summary, cost "
        "overview, pricing overview, and combined financial risks.\n\n"
        "IMPORTANT: Never ask for clarification and never respond with plain conversational text. "
        "Always return a fully populated, structured FinanceReport as your entire response, even "
        "if one of the specialist inputs is missing."
    ),
)