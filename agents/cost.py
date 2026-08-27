from pydantic_ai import Agent
from agents.model import get_groq_model
from state.schemas import CostAssessment
from tools.research import calculate_financial_metrics

# Model instance
model = get_groq_model()

# Cost Analysis Specialist Agent (reports to Finance Manager)
cost_agent = Agent(
    model=model,
    output_type=CostAssessment,
    retries=3,
    system_prompt=(
        "You are a meticulous Cost Analyst reporting to the Finance Manager.\n"
        "Your objective is to estimate the initial setup/capital expenditure, break down recurring "
        "operating expenses, estimate the break-even timeline, and flag cost-related risks for the "
        "business described in your assigned subtask.\n\n"
        "You may use the financial calculation tool to evaluate runway and break-even estimates.\n\n"
        "IMPORTANT: Never ask the user for clarification and never respond with plain conversational text. "
        "Even if the request is vague or generic, make reasonable, clearly-labeled assumptions and proceed. "
        "Always return a fully populated, structured CostAssessment as your entire response."
    ),
    tools=[calculate_financial_metrics],
)