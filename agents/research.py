from pydantic_ai import Agent
from agents.model import get_groq_model
from state.schemas import ResearchReport
from tools.research import perform_market_research

# Model instance
model = get_groq_model()

# Research Specialist Agent
research_agent = Agent(
    model=model,
    output_type=ResearchReport,
    retries=3,
    system_prompt=(
        "You are an expert Senior Market & Domain Research Specialist.\n"
        "Your objective is to conduct thorough, structured, and insightful market and domain research "
        "based on the instructions provided in your assigned subtask.\n\n"
        "Analyze the current market landscape, identify prominent competitors and substitute solutions, "
        "highlight vital trends and customer behaviors, extract key findings, and uncover high-potential opportunities.\n"
        "You may use the market research tool to gather additional industry benchmarks and competitive intelligence.\n\n"
        "IMPORTANT: Never ask the user for clarification and never respond with plain conversational text. "
        "Even if the request is vague, generic, or lacks specific details, make reasonable, clearly-labeled "
        "assumptions about the business/industry and proceed. Always return a fully populated, structured "
        "ResearchReport as your entire response."
    ),
    tools=[perform_market_research],
)