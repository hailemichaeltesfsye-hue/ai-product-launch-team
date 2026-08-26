from pydantic_ai import Agent
from agents.model import get_groq_model
from state.schemas import FinancialAssessment
from tools.research import calculate_financial_metrics

# Model instance
model = get_groq_model()

# Financial Feasibility & Modeling Specialist Agent
financial_agent = Agent(
    model=model,
    output_type=FinancialAssessment,
    retries=3,
    system_prompt=(
        "You are an experienced Chief Financial Officer (CFO) and Venture Analyst.\n"
        "Your objective is to build a realistic, grounded financial feasibility model based on the assigned subtask.\n\n"
        "Estimate initial setup and capital expenditure (capex), break down recurring operating expenses (opex), "
        "model diversified revenue streams and pricing structures, estimate the break-even timeline, "
        "and identify critical financial vulnerabilities or risk factors.\n"
        "You may use the financial calculation tool to evaluate runway and unit economics.\n\n"
        "IMPORTANT: Never ask the user for clarification and never respond with plain conversational text. "
        "Even if the request is vague or generic, make reasonable, clearly-labeled assumptions and proceed. "
        "Always return a fully populated, structured FinancialAssessment as your entire response."
    ),
    tools=[calculate_financial_metrics],
)