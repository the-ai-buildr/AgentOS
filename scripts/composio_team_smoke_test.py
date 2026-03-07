"""Smoke test for Composio wiring in Neo root team."""

from __future__ import annotations

import importlib

from agno.tools.mcp import MCPTools


def _load_dotenv() -> None:
    dotenv_module = importlib.import_module("dotenv")
    load_dotenv = getattr(dotenv_module, "load_dotenv")
    load_dotenv()


def main() -> None:
    _load_dotenv()

    from src.teams.neo_orchestrator import composio_agent, neo_team, tools_agent

    member_ids = [getattr(member, "id", "") for member in neo_team.members]
    if "neo-composio-agent" not in member_ids:
        raise RuntimeError("Composio agent is not registered in neo_team.members")

    composio_tools_in_tools_agent = [
        tool
        for tool in (tools_agent.tools or [])
        if isinstance(tool, MCPTools) and getattr(tool, "tool_name_prefix", None) == "composio"
    ]

    composio_tools_in_composio_agent = [
        tool
        for tool in (composio_agent.tools or [])
        if isinstance(tool, MCPTools) and getattr(tool, "tool_name_prefix", None) == "composio"
    ]

    if not composio_tools_in_tools_agent:
        raise RuntimeError("No Composio MCP tools were attached to tools_agent")
    if not composio_tools_in_composio_agent:
        raise RuntimeError("No Composio MCP tools were attached to composio_agent")

    print("Composio smoke test passed.")
    print(f"- neo_team has composio agent: {'neo-composio-agent' in member_ids}")
    print(f"- tools_agent composio tool count: {len(composio_tools_in_tools_agent)}")
    print(f"- composio_agent composio tool count: {len(composio_tools_in_composio_agent)}")


if __name__ == "__main__":
    main()
