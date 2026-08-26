from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from config.settings import settings


def get_groq_model() -> GroqModel:
    """Returns a configured GroqModel instance using application settings."""
    if settings.GROQ_API_KEY:
        provider = GroqProvider(api_key=settings.GROQ_API_KEY)
        return GroqModel(
            model_name=settings.GROQ_MODEL,
            provider=provider,
        )
    return GroqModel(model_name=settings.GROQ_MODEL)
