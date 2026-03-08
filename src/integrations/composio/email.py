"""Composio email-scoped MCP tool builder.

Returns MCPTools limited to email-related Composio actions (send, read,
search, draft, etc.).  Attach to agents that need email capabilities.
"""

from __future__ import annotations

import logging

from agno.tools.mcp import MCPTools
from agno.tools.mcp.params import StreamableHTTPClientParams

from .client import get_composio_session

log = logging.getLogger(__name__)


def build_composio_email_tools(
    *,
    tool_name_prefix: str = "composio_email",
) -> list[MCPTools]:
    """Build MCP tools scoped to Composio email actions."""
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
        log.warning("Failed to build Composio email MCP tools: %s", e)
        return []


__all__ = ["build_composio_email_tools"]
