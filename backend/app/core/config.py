"""
Core Application Configuration
==============================
Purpose:
    Manages global configuration parameters, environment variables,
    CORS policies, and third-party service credentials using Pydantic Settings.

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

    # Application Metadata
    APP_NAME: str = "AI Startup Idea Validator with Market Analysis Assistance"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Cross-Origin Resource Sharing (CORS)
    # Allows requests from Vite React frontend during development and Vercel in production
    ALLOWED_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    # Database Configuration (Future Milestones: PostgreSQL & SQLAlchemy)
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/startup_validator_db",
        description="PostgreSQL Database Connection URL",
    )

    # External AI & Search APIs (Future Milestones)
    TAVILY_API_KEY: str = Field(
        default="",
        description="API key for Tavily real-time web search service",
    )
    OPENAI_API_KEY: str = Field(
        default="",
        description="API key for OpenAI models (GPT-4o/mini)",
    )
    GEMINI_API_KEY: str = Field(
        default="",
        description="API key for Google Gemini models",
    )

    # Structured Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    def get_cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS whether provided as list or comma-separated string."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        return self.ALLOWED_ORIGINS


# Singleton settings instance
settings = Settings()
