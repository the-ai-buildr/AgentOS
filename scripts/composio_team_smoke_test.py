"""Smoke test for Neo team integration wiring.

Verifies that Composio tools and Agno SlackTools are attached to the
correct agents after the communications consolidation.
"""

from __future__ import annotations

import importlib

from agno.tools.slack import SlackTools


def _load_dotenv() -> None:
    dotenv_module = importlib.import_module("dotenv")
    load_dotenv = getattr(dotenv_module, "load_dotenv")
    load_dotenv()


def _has_tool_type(agent, tool_type: type) -> bool:
    """Check whether *agent* has at least one tool of the given type."""
    return any(isinstance(t, tool_type) for t in (agent.tools or []))


def _composio_tools_count(agent) -> int:
    """Count Composio-provided tools on *agent*."""
    return sum(
        1
        for t in (agent.tools or [])
        if type(t).__module__.startswith("composio")
    )


def main() -> None:
    _load_dotenv()

    from src.teams.neo_orchestrator import (
        communication_agent,
        neo_team,
        tools_agent,
    )

    # tools_agent should have broad Composio tools.
    tools_composio = _composio_tools_count(tools_agent)
    if not tools_composio:
        raise RuntimeError("No Composio tools attached to tools_agent")

    # communication_agent should have email-scoped Composio tools.
    comm_composio = _composio_tools_count(communication_agent)
    if not comm_composio:
        raise RuntimeError("No Composio email tools attached to communication_agent")

    # SlackTools should be on communication_agent (the unified comms hub).
    if not _has_tool_type(communication_agent, SlackTools):
        raise RuntimeError("SlackTools not attached to communication_agent")

    # tools_agent should NOT have SlackTools (comms agent owns Slack).
    if _has_tool_type(tools_agent, SlackTools):
        raise RuntimeError("SlackTools should not be on tools_agent — use communication_agent")

    # Monolithic composio_agent and workspace_channel_agent should NOT be team members.
    member_ids = [getattr(m, "id", "") for m in neo_team.members]
    for stale_id in ("neo-composio-agent", "neo-workspace-channel-agent"):
        if stale_id in member_ids:
            raise RuntimeError(f"{stale_id} still registered in neo_team")

    print("Integration smoke test passed.")
    print(f"  communication_agent  — composio tools: {comm_composio}, SlackTools: yes")
    print(f"  tools_agent          — composio tools: {tools_composio}, SlackTools: no")


if __name__ == "__main__":
    main()
