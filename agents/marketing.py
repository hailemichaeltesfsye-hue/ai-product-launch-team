from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from config.settings import settings
from state.schemas import MarketingPlan

# Setup Groq Model
model = GroqModel("llama-3.3-70b-versatile", api_key=settings.GROQ_API_KEY)

marketing_agent = Agent(
    model=model,
    result_type=MarketingPlan,
    system_prompt=(
        "You are an expert Marketing Lead. Based on the provided ProductBrief, "
        "define a strategic MarketingPlan."
    ),
)
