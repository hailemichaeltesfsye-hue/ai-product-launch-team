from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Skeletal configuration settings loaded via Pydantic Settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    GROQ_API_KEY: Optional[str] = None
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "app.log"


settings = Settings()
