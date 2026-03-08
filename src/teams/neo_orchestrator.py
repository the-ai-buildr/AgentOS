"""Top-level Neo orchestration team and pulse dispatcher agent."""

from agno.agent import Agent
from agno.team import Team
from agno.team.mode import TeamMode
from agno.tools.duckdb import DuckDbTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools

from src.models import OpenRouter
from src.prompts import load_prompt
from src.teams.dev_team import dev_team
from src.teams.research_team import research_team
from src.teams.shared import duckdb_path, neo_skills, neo_team_learning_store
from src.tools.mcp_tools import build_mcp_tools
from src.tools.slack_tools import send_workspace_webhook_update

# Reuse one shared MCP tool set across Neo agents to avoid duplicate
# FastMCP stdio server processes during startup.
shared_mcp_tools = build_mcp_tools()

# Neo Communication Agent
communication_agent = Agent(
    id="neo-communication-agent",
    name="Communication Agent",
    role="User-facing intake specialist. Asks probing questions, gathers context, and produces structured briefs.",
    model=OpenRouter.create(model_type="claude-sonnet"),
    instructions=load_prompt("communication_agent.md"),
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

# Neo Project Manager
project_manager = Agent(
    id="neo-project-manager",
    name="Project Manager",
    role="Task decomposition and planning specialist. Breaks objectives into structured task plans with acceptance criteria and dependencies.",
    model=OpenRouter.create(model_type="claude-sonnet"),
    instructions=load_prompt("project_manager.md"),
    tools=[ReasoningTools(add_instructions=True)],
    skills=neo_skills,
    add_datetime_to_context=True,
    markdown=True,
)

# Neo Workspace Channel Agent
workspace_channel_agent = Agent(
    id="neo-workspace-channel-agent",
    name="Workspace Channel Agent",
    role="Slack #workspace specialist. Turns requests into executable plans, tracks blockers, and returns concise action-oriented updates.",
    model=OpenRouter.create(model_type="claude-sonnet"),
    instructions=load_prompt("workspace_channel_agent.md"),
    tools=[ReasoningTools(add_instructions=True), send_workspace_webhook_update, *shared_mcp_tools],
    skills=neo_skills,
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

# Neo Plane Agent
plane_agent = Agent(
    id="neo-plane-agent",
    name="Plane Agent",
    role="Plane system-of-record operator. Creates, updates, and queries projects, issues, prompts, and templates in Plane.",
    model=OpenRouter.create(model_type="gemini-flash"),
    instructions=load_prompt("plane_agent.md"),
    tools=shared_mcp_tools,
    skills=neo_skills,
    add_datetime_to_context=True,
    markdown=True,
)

# Neo Tools Agent
tools_agent = Agent(
    id="neo-tools-agent",
    name="Tools Agent",
    role="System tool executor. Has access to all MCP tools, web search, and data tools for executing actions on behalf of the team.",
    model=OpenRouter.create(model_type="gemini-flash"),
    instructions=load_prompt("tools_agent.md"),
    tools=[
        DuckDuckGoTools(),
        DuckDbTools(db_path=duckdb_path),
        send_workspace_webhook_update,
        *shared_mcp_tools,
    ],
    add_datetime_to_context=True,
    markdown=True,
)

# Neo Content Agent
content_agent = Agent(
    id="neo-exec-content",
    name="Content Agent",
    role="Writing and communication specialist. Produces status updates, documentation, stakeholder summaries, and task completion narratives.",
    model=OpenRouter.create(model_type="claude-sonnet"),
    instructions=load_prompt("exec_content_agent.md"),
    add_datetime_to_context=True,
    markdown=True,
)

# Neo Pulse Agent
pulse_agent = Agent(
    id="neo-pulse",
    name="Pulse Dispatcher",
    role="Autonomous operations heartbeat. Scans Plane for ready work, dispatches to team members, detects stalled tasks, and logs operational intelligence.",
    model=OpenRouter.create(model_type="gemini-flash"),
    instructions=load_prompt("pulse_dispatcher.md"),
    tools=shared_mcp_tools,
    skills=neo_skills,
    learning=neo_team_learning_store,
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    add_memories_to_context=True,
    markdown=True,
)

# Neo Team
neo_team = Team(
    id="neo-team",
    name="Neo Orchestrator Team",
    mode=TeamMode.coordinate,
    model=OpenRouter.create(model_type="claude-sonnet"),
    members=[
        communication_agent,
        workspace_channel_agent,
        project_manager,
        plane_agent,
        tools_agent,
        dev_team,
        research_team,
        content_agent,
    ],
    instructions=load_prompt("neo_agent.md"),
    learning=neo_team_learning_store,
    show_members_responses=True,
    enable_session_summaries=True,
    enable_agentic_memory=True,
    enable_agentic_state=True,
    add_session_state_to_context=True,
    add_memories_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    add_datetime_to_context=True,
    markdown=True,
)


# if __name__ == "__main__":
#     neo_team.print_response("What is the Neo Team?", stream=True)


__all__ = [
    "neo_team",
    "pulse_agent",
    "communication_agent",
    "workspace_channel_agent",
    "project_manager",
    "plane_agent",
    "tools_agent",
    "content_agent",
]
