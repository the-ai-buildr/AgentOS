"""Composio Hosted MCP tool builder used by Neo team agents."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any

from agno.tools.mcp import MCPTools
from agno.tools.mcp.params import StreamableHTTPClientParams

log = logging.getLogger(__name__)
_DISABLED_VALUES = {"1", "true", "yes"}


def _is_disabled(env_var: str) -> bool:
    return os.getenv(env_var, "").strip().lower() in _DISABLED_VALUES


def _resolve_external_user_id(
    *,
    primary_env_var: str,
    legacy_env_var: str,
    default_user: str,
 ) -> str:
    primary = os.getenv(primary_env_var, "").strip()
    if primary:
        return primary
    legacy = os.getenv(legacy_env_var, "").strip()
    if legacy:
        return legacy
    return default_user


@lru_cache(maxsize=1)
def _create_hosted_mcp_connection(api_key: str, external_user_id: str) -> tuple[str, dict[str, Any]]:
    composio_module = __import__("composio")
    Composio = getattr(composio_module, "Composio")
    composio_client = Composio(api_key=api_key)
    session = composio_client.create(user_id=external_user_id)
    return session.mcp.url, dict(session.mcp.headers or {})


def build_composio_mcp_tools(
    *,
    disable_env_var: str = "COMPOSIO_DISABLED",
    api_key_env_var: str = "COMPOSIO_API_KEY",
    external_user_id_env_var: str = "COMPOSIO_EXTERNAL_USER_ID",
    legacy_external_user_id_env_var: str = "COMPOSIO_EXT_USER_ID",
    default_external_user_id: str = "agentos-default-user",
    tool_name_prefix: str = "composio",
) -> list[MCPTools]:
    """Build authenticated MCP tools from a Composio hosted session."""
    if _is_disabled(disable_env_var):
        return []

    api_key = os.getenv(api_key_env_var, "").strip()
    if not api_key:
        return []

    external_user_id = _resolve_external_user_id(
        primary_env_var=external_user_id_env_var,
        legacy_env_var=legacy_external_user_id_env_var,
        default_user=default_external_user_id,
    )

    try:
        url, headers = _create_hosted_mcp_connection(api_key, external_user_id)
    except ModuleNotFoundError:
        log.warning("Composio SDK is not installed; skipping Composio MCP tools.")
        return []
    except Exception as e:
        log.warning("Failed to initialize Composio Hosted MCP tools: %s", e)
        return []

    try:
        server_params = StreamableHTTPClientParams(url=url, headers=headers)
        return [
            MCPTools(
                url=url,
                transport="streamable-http",
                server_params=server_params,
                tool_name_prefix=tool_name_prefix,
            )
        ]
    except Exception as e:
        log.warning("Failed to build Composio MCP tool from hosted session: %s", e)
        return []


__all__ = ["build_composio_mcp_tools"]
