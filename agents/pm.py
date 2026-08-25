from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from config.settings import settings
from state.schemas import ProductBrief

# Setup Groq Model (Note: will fall back to mock or require api_key)
model = GroqModel("llama-3.3-70b-versatile", api_key=settings.GROQ_API_KEY)

pm_agent = Agent(
    model=model,
    result_type=ProductBrief,
    system_prompt=(
        "You are an experienced Product Manager. Convert a given product "
        "idea into a detailed, structured ProductBrief."
    ),
)
