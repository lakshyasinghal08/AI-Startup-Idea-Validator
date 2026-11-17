"""
Core Application Configuration
==============================
Purpose:
    Manages global configuration parameters, environment variables,
    CORS policies, and external service credentials using Pydantic Settings.

Milestone Notes:
    - Milestone 1: Baseline configuration and environment variable loading.
    - Future Milestones: Integrate database connection pooling, LLM provider credentials,
      and OAuth2 secret keys.
"""

from typing import List, Union
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized settings loaded from environment variables and `.env` file.
    Default values allow the application to start in development mode seamlessly.
    """

    # Application Metadata & Server Configuration
    APP_NAME: str = "AI-Startup-Idea-Validator"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    API_PREFIX: str = "/api/v1"

    # External AI & Search APIs (Milestone 2 & 3 Placeholders)
    OPENAI_API_KEY: str = Field(
        default="",
        description="API key for OpenAI models (GPT-4o/mini)",
    )
    GEMINI_API_KEY: str = Field(
        default="",
        description="API key for Google Gemini models",
    )
    TAVILY_API_KEY: str = Field(
        default="",
        description="API key for Tavily real-time web search service",
    )

    # Frontend URL & CORS Configuration
    FRONTEND_URL: str = Field(
        default="http://localhost:5173",
        description="Origin URL of the frontend application",
    )

    # Structured Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def API_V1_PREFIX(self) -> str:
        """Alias for backward compatibility with router prefixing."""
        return self.API_PREFIX

    def get_cors_origins(self) -> List[str]:
        """
        Builds the list of allowed CORS origins including the configured
        FRONTEND_URL and standard local development ports.
        """
        origins = {
            self.FRONTEND_URL.rstrip("/"),
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        }
        return list(origins)


# Singleton settings instance
settings = Settings()


if __name__ == "__main__":
    print(f"Loaded Settings: App='{settings.APP_NAME}', Env='{settings.ENVIRONMENT}', Port={settings.PORT}")
