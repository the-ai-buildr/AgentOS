from os import getenv
from pathlib import Path

from agno.agent import Agent
from agno.learn import (
    LearnedKnowledgeConfig,
    LearningMachine,
    LearningMode,
    UserMemoryConfig,
    UserProfileConfig,
)
from agno.team import Team
from agno.team.mode import TeamMode
from agno.tools.duckdb import DuckDbTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools

from db import get_postgres_db
from src.models import OpenRouter
from src.prompts import load_prompt
from src.tools.mcp_tools import build_mcp_tools

# ============================================================================
# Shared infrastructure
# ============================================================================

db = get_postgres_db()
data_dir = Path(getenv("DATA_DIR", "/data"))
data_dir.mkdir(parents=True, exist_ok=True)
duckdb_path = str(data_dir / "neo_team.db")

# ============================================================================
# Learning Machine (shared across the team)
# ============================================================================

learned_knowledge_config = LearnedKnowledgeConfig(
    agent_can_save=True,
    agent_can_search=True,
    enable_agent_tools=True,
    instructions="You are a learning machine that can save and search learned knowledge.",
    mode=LearningMode.AGENTIC,
)

user_profile_config = UserProfileConfig(
    agent_can_update_profile=True,
    enable_agent_tools=True,
    enable_update_profile=True,
    mode=LearningMode.AGENTIC,
    instructions="You are a user profile that can save and search learned knowledge.",
)

user_memory_config = UserMemoryConfig(
    enable_agent_tools=True,
    enable_update_memory=True,
    enable_add_memory=True,
    mode=LearningMode.AGENTIC,
    instructions="You are a user memory that can save and search learned knowledge.",
)

neo_team_learning_store = LearningMachine(
    namespace="global",
    model=OpenRouter.create(model_type="claude-sonnet"),
    db=db,
    session_context=True,
    user_profile=user_profile_config,
    user_memory=user_memory_config,
    learned_knowledge=learned_knowledge_config,
)

# ============================================================================
# Dev Sub-Team
# ============================================================================

dev_implementer = Agent(
    id="neo-dev-implementer",
    name="Dev Implementer",
    role="Build solutions and implement tasks according to the approach set by the Dev Lead.",
    model=OpenRouter.create(model_type="claude-sonnet"),
    instructions=load_prompt("dev_implementer.md"),
    add_datetime_to_context=True,
    markdown=True,
)

dev_reviewer = Agent(
    id="neo-dev-reviewer",
    name="Dev Reviewer",
    role="Validate implementation output against acceptance criteria and report pass/fail.",
    model=OpenRouter.create(model_type="grok"),
    instructions=load_prompt("dev_reviewer.md"),
    add_datetime_to_context=True,
    markdown=True,
)

dev_team = Team(
    id="neo-dev-team",
    name="Dev Team",
    role="Implementation, debugging, and technical problem-solving. Receives defined tasks with acceptance criteria and delivers verified results.",
    mode=TeamMode.coordinate,
    model=OpenRouter.create(model_type="claude-sonnet"),
    members=[dev_implementer, dev_reviewer],
    instructions=load_prompt("dev_lead.md"),
    show_members_responses=True,
    markdown=True,
)

# ============================================================================
# Research Sub-Team
# ============================================================================

deep_researcher = Agent(
    id="neo-deep-researcher",
    name="Deep Researcher",
    role="Perform deep web-grounded research with citations using Perplexity.",
    model=OpenRouter.create(model_type="perplexity-reasoning"),
    instructions=load_prompt("deep_researcher.md"),
    add_datetime_to_context=True,
    markdown=True,
)

research_analyst = Agent(
    id="neo-research-analyst",
    name="Research Analyst",
    role="Evaluate evidence quality, grade sources, and produce structured analysis.",
    model=OpenRouter.create(model_type="claude-sonnet"),
    instructions=load_prompt("research_analyst.md"),
    add_datetime_to_context=True,
    markdown=True,
)

research_team = Team(
    id="neo-research-team",
    name="Research Team",
    role="Evidence-based discovery, deep research, and synthesis. Produces structured findings reports with source grading and recommendations.",
    mode=TeamMode.coordinate,
    model=OpenRouter.create(model_type="claude-sonnet"),
    members=[deep_researcher, research_analyst],
    instructions=load_prompt("research_lead.md"),
    show_members_responses=True,
    markdown=True,
)

# ============================================================================
# Top-level member agents
# ============================================================================

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

project_manager = Agent(
    id="neo-project-manager",
    name="Project Manager",
    role="Task decomposition and planning specialist. Breaks objectives into structured task plans with acceptance criteria and dependencies.",
    model=OpenRouter.create(model_type="claude-sonnet"),
    instructions=load_prompt("project_manager.md"),
    tools=[ReasoningTools(add_instructions=True)],
    add_datetime_to_context=True,
    markdown=True,
)

plane_agent = Agent(
    id="neo-plane-agent",
    name="Plane Agent",
    role="Plane system-of-record operator. Creates, updates, and queries projects, issues, prompts, and templates in Plane.",
    model=OpenRouter.create(model_type="gemini-flash"),
    instructions=load_prompt("plane_agent.md"),
    tools=build_mcp_tools(),
    add_datetime_to_context=True,
    markdown=True,
)

tools_agent = Agent(
    id="neo-tools-agent",
    name="Tools Agent",
    role="System tool executor. Has access to all MCP tools, web search, and data tools for executing actions on behalf of the team.",
    model=OpenRouter.create(model_type="gemini-flash"),
    instructions=load_prompt("tools_agent.md"),
    tools=[
        DuckDuckGoTools(),
        DuckDbTools(db_path=duckdb_path),
        *build_mcp_tools(),
    ],
    add_datetime_to_context=True,
    markdown=True,
)

content_agent = Agent(
    id="neo-exec-content",
    name="Content Agent",
    role="Writing and communication specialist. Produces status updates, documentation, stakeholder summaries, and task completion narratives.",
    model=OpenRouter.create(model_type="claude-sonnet"),
    instructions=load_prompt("exec_content_agent.md"),
    add_datetime_to_context=True,
    markdown=True,
)

# ============================================================================
# Neo Team (top-level coordinator)
# ============================================================================

neo_team = Team(
    id="neo-team",
    name="Neo Orchestrator Team",
    mode=TeamMode.coordinate,
    model=OpenRouter.create(model_type="claude-sonnet"),
    members=[
        communication_agent,
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

if __name__ == "__main__":
    neo_team.print_response("What is the Neo Team?", stream=True)
