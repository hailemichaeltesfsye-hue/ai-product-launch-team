from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from config.settings import settings
from state.schemas import TechnicalArchitecture

# Setup Groq Model
model = GroqModel("llama-3.3-70b-versatile", api_key=settings.GROQ_API_KEY)

tech_lead_agent = Agent(
    model=model,
    result_type=TechnicalArchitecture,
    system_prompt=(
        "You are an expert Technical Lead. Review the provided ProductBrief "
        "and produce a comprehensive TechnicalArchitecture layout."
    ),
)
