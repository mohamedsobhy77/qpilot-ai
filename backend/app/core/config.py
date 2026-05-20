"""
app/core/config.py

Central configuration using pydantic-settings.
All settings are read from environment variables (or .env file).
Import `settings` anywhere in the app — never read os.environ directly.
"""

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────
    app_name: str = "QPilot AI"
    app_env: str = "development"
    debug: bool = False
    secret_key: str

    # ── Database ─────────────────────────────────────────────
    database_url: str  # postgresql+asyncpg://...

    # ── JWT ──────────────────────────────────────────────────
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ── OpenAI ───────────────────────────────────────────────
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_max_tokens: int = 4096
    openai_temperature: float = 0.3

    # ── Jira ─────────────────────────────────────────────────
    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""
    jira_project_key: str = "QP"

    # ── GitHub ───────────────────────────────────────────────
    github_token: str = ""
    github_owner: str = ""
    github_repo: str = "qpilot-automation-scripts"

    # ── Slack ────────────────────────────────────────────────
    slack_webhook_url: str = ""

    # ── n8n ──────────────────────────────────────────────────
    n8n_webhook_base_url: str = "http://localhost:5678/webhook"

    # ── CORS ─────────────────────────────────────────────────
    cors_origins: List[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton — settings object is created once per process."""
    return Settings()


# Convenience alias used throughout the app
settings = get_settings()
