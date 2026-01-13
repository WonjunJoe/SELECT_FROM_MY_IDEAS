"""
Centralized configuration management for Select From My Ideas.

Usage:
    from config import settings

    api_key = settings.openai_api_key
    model = settings.llm_model
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    llm_model: str = Field(default="gpt-4o", description="LLM model to use")
    llm_temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="LLM sampling temperature"
    )
    llm_max_tokens: int | None = Field(
        default=None, description="Max tokens for LLM response"
    )

    # Server Configuration
    server_host: str = Field(default="0.0.0.0", description="Server host")
    server_port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    server_reload: bool = Field(default=True, description="Enable hot reload")

    # Session Configuration
    max_rounds: int = Field(
        default=5, ge=1, le=10, description="Maximum conversation rounds"
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )
    log_to_file: bool = Field(default=True, description="Enable file logging")
    log_to_console: bool = Field(default=True, description="Enable console logging")

    # Database Configuration
    db_path: str = Field(default="data/sessions.db", description="SQLite database path")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance for easy import
settings = get_settings()
