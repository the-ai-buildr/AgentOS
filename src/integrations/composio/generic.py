"""Catch-all Composio MCP tool builder.

Returns an MCPTools instance with access to *all* Composio actions.
Use this when an agent needs broad Composio access rather than a
domain-scoped subset.
"""

from __future__ import annotations

import logging

from agno.tools.mcp import MCPTools
from agno.tools.mcp.params import StreamableHTTPClientParams

from .client import get_composio_session

log = logging.getLogger(__name__)


def build_composio_tools(
    *,
    tool_name_prefix: str = "composio",
 ) -> list[MCPTools]:
    """Build MCP tools with access to all Composio actions."""
    session = get_composio_session()
    if session is None:
        return []

    url, headers = session
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
        log.warning("Failed to build generic Composio MCP tools: %s", e)
        return []


__all__ = ["build_composio_tools"]
