"""Composio integration — domain-scoped MCP tool builders.

Usage::

    from src.integrations.composio import build_composio_tools
    from src.integrations.composio import build_composio_email_tools

Attach the returned ``list[MCPTools]`` to any agent's ``tools`` list.
"""

from .client import get_composio_session, is_composio_disabled
from .email import build_composio_email_tools
from .generic import build_composio_tools

__all__ = [
    "get_composio_session",
    "is_composio_disabled",
    "build_composio_tools",
    "build_composio_email_tools",
]
