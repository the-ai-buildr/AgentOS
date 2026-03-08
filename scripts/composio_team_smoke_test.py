"""Smoke test for per-agent Composio wiring in Neo team.

Verifies that domain-scoped Composio MCP tools are attached to the
correct individual agents rather than a single monolithic Composio agent.
"""

from __future__ import annotations

import importlib

from agno.tools.mcp import MCPTools


def _load_dotenv() -> None:
    dotenv_module = importlib.import_module("dotenv")
    load_dotenv = getattr(dotenv_module, "load_dotenv")
    load_dotenv()


def _composio_tools_on(agent, *, prefix: str | None = None) -> list[MCPTools]:
    """Return Composio MCPTools attached to *agent*, optionally filtered by prefix."""
    return [
        tool
        for tool in (agent.tools or [])
        if isinstance(tool, MCPTools)
        and (prefix is None or getattr(tool, "tool_name_prefix", None) == prefix)
    ]


def main() -> None:
    _load_dotenv()

    from src.teams.neo_orchestrator import communication_agent, neo_team, tools_agent

    # tools_agent should have the generic (all-actions) Composio tools.
    generic = _composio_tools_on(tools_agent, prefix="composio")
    if not generic:
        raise RuntimeError("No generic Composio MCP tools attached to tools_agent")

    # communication_agent should have email-scoped Composio tools.
    email = _composio_tools_on(communication_agent, prefix="composio_email")
    if not email:
        raise RuntimeError("No Composio email MCP tools attached to communication_agent")

    # Monolithic composio_agent should NOT exist as a team member.
    member_ids = [getattr(m, "id", "") for m in neo_team.members]
    if "neo-composio-agent" in member_ids:
        raise RuntimeError(
            "Monolithic composio_agent still registered in neo_team — "
            "should be replaced by per-agent Composio tools"
        )

    print("Composio integration smoke test passed.")
    print(f"  tools_agent          — generic composio tools: {len(generic)}")
    print(f"  communication_agent  — email composio tools:   {len(email)}")


if __name__ == "__main__":
    main()
