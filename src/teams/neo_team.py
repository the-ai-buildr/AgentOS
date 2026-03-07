from agno.team import Team
from agno.agent import Agent
from agno.learn import (
    LearnedKnowledgeConfig,
    LearnedKnowledge,
    LearningMachine,
    LearningMode,
    UserMemoryConfig,
    UserProfileConfig,
)
from agno.learn.stores import learned_knowledge
from src.prompts import load_prompt
from src.models import OpenRouter
from src.tools.mcp_tools import build_mcp_tools
from db import get_postgres_db

# Learning Machine Configuration
learned_knowledge_config = LearnedKnowledgeConfig(
    agent_can_save=True,
    agent_can_search=True,
    enable_agent_tools=True,
    instructions="You are a learning machine that can save and search learned knowledge.",
    mode=LearningMode.AGENTIC
)

# User Profile Configuration
user_profile_config = UserProfileConfig(
    agent_can_update_profile=True,
    enable_agent_tools=True,
    enable_update_profile=True,
    mode=LearningMode.AGENTIC,
    instructions="You are a user profile that can save and search learned knowledge.",
)

# User Memory Configuration
user_memory_config = UserMemoryConfig(
    enable_agent_tools=True,
    enable_update_memory=True,
    enable_add_memory=True,
    mode=LearningMode.AGENTIC,
    instructions="You are a user memory that can save and search learned knowledge.",
)

# Learning Machine Configuration
neo_team_learning_store = LearningMachine(
    namespace="global",
    model=OpenRouter.create(model_type="claude-sonnet"),
    db=get_postgres_db(),
    session_context=True,
    user_profile=user_profile_config,
    user_memory=user_memory_config,
    learned_knowledge=learned_knowledge_config,
)

# Neo Chief of Staff
# chief_of_staff = Agent(
#     id="neo-chief-of-staff",
#     name="Neo Chief of Staff",
#     model=OpenRouter.create(model_type="claude-sonnet"),
#     db=get_postgres_db(),
#     instructions=load_prompt("neo_chief_of_staff.md"),
#     tools=build_mcp_tools(default_urls=[]),
#     add_history_to_context=True,
#     num_history_runs=5,
#     add_datetime_to_context=True,
#     markdown=True,
# )

# Neo Pulse Dispatcher
pulse_dispatcher = Agent(
    id="neo-pulse-dispatcher",
    name="Neo Pulse Dispatcher",
    model=OpenRouter.create(model_type="claude-sonnet"),
    db=get_postgres_db(),
    instructions=load_prompt("neo_pulse_dispatcher.md"),
    tools=build_mcp_tools(default_urls=[]),
)

# Neo Agent
neo_agent = Agent(
    id="neo-agent",
    name="Neo Agent",
    model=OpenRouter.create(model_type="claude-sonnet"),
    instructions="You are the Neo Agent, you are the main agent for the Neo Team.",
    add_session_state_to_context = True,
    add_memories_to_context = True,
    learning=neo_team_learning_store,
    add_history_to_context=True,
    num_history_runs=5,
    add_datetime_to_context=True,
)

slack_agent = Agent(
    id="slack-agent",
    name="Slack Agent",
    model=OpenRouter.create(model_type="claude-sonnet"),
    instructions=load_prompt("slack_agent.md"),
    learning=neo_team_learning_store,
    add_history_to_context=True,
    num_history_runs=5,
    add_datetime_to_context=True,
)

# Neo Team
neo_team = Team(    
    id="neo-team",
    name="Neo Orchestrator Team",
    members=[neo_agent, pulse_dispatcher, slack_agent],
    enable_session_summaries=True,
    enable_agentic_memory=True,
    enable_agentic_state=True,
    add_history_to_context=True,
    num_history_runs=5,
    add_datetime_to_context=True,
    markdown=True,
)

if __name__ == "__main__":
    neo_team.print_response("What is the Neo Team?", stream=True)
