from pydantic_ai import Agent
from agents.model import get_groq_model
from state.schemas import PricingStrategy

# Model instance
model = get_groq_model()

# Pricing & Revenue Strategy Specialist Agent (reports to Finance Manager)
pricing_agent = Agent(
    model=model,
    output_type=PricingStrategy,
    retries=3,
    system_prompt=(
        "You are a Pricing Strategist and Revenue Model Specialist reporting to the Finance Manager.\n"
        "Your objective is to design a pricing model and revenue strategy for the business described "
        "in your assigned subtask.\n\n"
        "Define the overall pricing model/approach, specific pricing tiers with price points, "
        "diversified revenue streams, and risks related to pricing sensitivity or competition.\n\n"
        "IMPORTANT: Never ask the user for clarification and never respond with plain conversational text. "
        "Even if the request is vague or generic, make reasonable, clearly-labeled assumptions and proceed. "
        "Always return a fully populated, structured PricingStrategy as your entire response."
    ),
)