from dataclasses import dataclass
from functools import lru_cache
from os import getenv
from typing import Optional


def _to_bool(value: Optional[str], default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: Optional[str], default: int) -> int:
    if value is None:
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    """Centralized runtime settings loaded from environment variables."""

    runtime_env: str = "prd"
    agentos_name: str = "The Ai Buildr - AgentOS"
    scheduler_enabled: bool = True
    scheduler_poll_interval: int = 15
    tracing: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached app settings instance."""
    return Settings(
        runtime_env=getenv("RUNTIME_ENV", "prd"),
        agentos_name=getenv("AGENTOS_NAME", "The Ai Buildr - AgentOS"),
        scheduler_enabled=_to_bool(getenv("SCHEDULER_ENABLED"), True),
        scheduler_poll_interval=_to_int(getenv("SCHEDULER_POLL_INTERVAL"), 15),
        tracing=_to_bool(getenv("AGENTOS_TRACING"), True),
    )
