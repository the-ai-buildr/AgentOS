"""Simple MCP tool builders used across agents and teams."""

import logging
import os
from typing import Iterable

from agno.tools.mcp import MCPTools

log = logging.getLogger(__name__)
_DISABLED_VALUES = {"1", "true", "yes"}
_EMPTY_VALUES = {"none", "disabled", "false", "0"}


def _parse_urls(raw_urls: str) -> list[str]:
    """Parse comma/newline separated URLs into a deduplicated list."""
    urls: list[str] = []
    for part in raw_urls.replace("\n", ",").split(","):
        url = part.strip().strip('"').strip("'")
        if url and url.startswith(("http://", "https://")) and url not in urls:
            urls.append(url)
    return urls


def _get_urls_from_env(env_var: str, default_urls: Iterable[str] | None) -> list[str]:
    raw = os.getenv(env_var, "").strip().lower()
    if raw in _EMPTY_VALUES:
        return []
    urls = _parse_urls(os.getenv(env_var, ""))
    return urls if urls else list(default_urls or [])


def build_mcp_tools(
    *,
    env_var: str = "MCP_SERVER_URLS",
    default_urls: Iterable[str] | None = None,
    disable_env_var: str = "MCP_DISABLED",
 ) -> list[MCPTools]:
    """Build MCP tools from env-provided URL list."""
    if os.getenv(disable_env_var, "").strip().lower() in _DISABLED_VALUES:
        return []

    urls = _get_urls_from_env(env_var=env_var, default_urls=default_urls)
    tools: list[MCPTools] = []
    for url in urls:
        try:
            tools.append(MCPTools(url=url, transport="streamable-http"))
        except Exception as e:
            log.warning("Skipping MCP server %s: %s", url, e)

    return tools


__all__ = ["build_mcp_tools"]
