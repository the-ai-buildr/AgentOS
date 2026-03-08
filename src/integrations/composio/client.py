"""Composio Hosted MCP session management.

Single source of truth for Composio authentication and session creation.
All domain-specific tool builders import from here.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any

log = logging.getLogger(__name__)

_DISABLED_VALUES = {"1", "true", "yes"}


def is_composio_disabled(
    env_var: str = "COMPOSIO_DISABLED",
) -> bool:
    return os.getenv(env_var, "").strip().lower() in _DISABLED_VALUES


def _resolve_external_user_id(
    *,
    primary_env_var: str = "COMPOSIO_EXTERNAL_USER_ID",
    legacy_env_var: str = "COMPOSIO_EXT_USER_ID",
    default_user: str = "agentos-default-user",
 ) -> str:
    primary = os.getenv(primary_env_var, "").strip()
    if primary:
        return primary
    legacy = os.getenv(legacy_env_var, "").strip()
    if legacy:
        return legacy
    return default_user


@lru_cache(maxsize=1)
def _create_hosted_mcp_connection(
    api_key: str, external_user_id: str
 ) -> tuple[str, dict[str, Any]]:
    composio_module = __import__("composio")
    Composio = getattr(composio_module, "Composio")
    composio_client = Composio(api_key=api_key)
    session = composio_client.create(user_id=external_user_id)
    return session.mcp.url, dict(session.mcp.headers or {})


def get_composio_session(
    *,
    api_key_env_var: str = "COMPOSIO_API_KEY",
 ) -> tuple[str, dict[str, Any]] | None:
    """Return ``(url, headers)`` for a Composio Hosted MCP session.

    Returns ``None`` when Composio is disabled, the API key is missing, or
    the SDK cannot be loaded.
    """
    if is_composio_disabled():
        return None

    api_key = os.getenv(api_key_env_var, "").strip()
    if not api_key:
        return None

    external_user_id = _resolve_external_user_id()

    try:
        return _create_hosted_mcp_connection(api_key, external_user_id)
    except ModuleNotFoundError:
        log.warning("Composio SDK is not installed; skipping Composio MCP tools.")
        return None
    except Exception as e:
        log.warning("Failed to initialize Composio Hosted MCP session: %s", e)
        return None


__all__ = ["get_composio_session", "is_composio_disabled"]
