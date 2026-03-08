from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized runtime settings loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    runtime_env: str = Field(default="prd", validation_alias="RUNTIME_ENV")
    agentos_name: str = Field(default="The Ai Buildr - AgentOS", validation_alias="AGENTOS_NAME")
    scheduler_enabled: bool = Field(default=True, validation_alias="SCHEDULER_ENABLED")
    scheduler_poll_interval: int = Field(default=15, validation_alias="SCHEDULER_POLL_INTERVAL")
    tracing: bool = Field(default=True, validation_alias="AGENTOS_TRACING")

    slack_bot_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SLACK_BOT_TOKEN", "SLACK_TOKEN"),
    )
    slack_signing_secret: str | None = Field(default=None, validation_alias="SLACK_SIGNING_SECRET")
    slack_workspace_channel_id: str | None = Field(default=None, validation_alias="SLACK_WORKSPACE_CHANNEL_ID")
    slack_workspace_webhook_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SLACK_WORKSPACE_WEBHOOK_URL", "SLACK_WEBHOOK_URL"),
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached app settings instance."""
    return Settings()

