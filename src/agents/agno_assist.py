"""Primary personal-assistant agent with memory and tool access."""

from os import getenv
from pathlib import Path

from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.learn import (
    LearnedKnowledgeConfig,
    LearningMachine,
    LearningMode,
    UserMemoryConfig,
    UserProfileConfig,
)
from agno.tools.duckdb import DuckDbTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.pgvector import PgVector, SearchType

from src.prompts import load_prompt
from src.tools.mcp_tools import build_mcp_tools
from db import db_url, get_postgres_db
from src.models import OpenRouter

# ============================================================================
# Setup
# ============================================================================
agent_db = get_postgres_db(contents_table="agno_assist_contents")
data_dir = Path(getenv("DATA_DIR", "/data"))
data_dir.mkdir(parents=True, exist_ok=True)

duckdb_path = str(data_dir / "agno_assist.db")

# Knowledge base for semantic search and learnings
agno_assist_knowledge = Knowledge(
    name="Agno Assist Knowledge",
    vector_db=PgVector(
        db_url=db_url,
        table_name="agno_assist_knowledge",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    contents_db=agent_db,
)

# ============================================================================
# Create Agent
# ============================================================================
agno_assist = Agent(
    id="agno-assist",
    name="Agno Assist",
    model=OpenRouter.create("openai/gpt-5.4"),
    db=agent_db,
    instructions=load_prompt("agno_assist.md"),
    # Learning
    learning=LearningMachine(
        knowledge=agno_assist_knowledge,
        db=agent_db,
        user_profile=UserProfileConfig(mode=LearningMode.AGENTIC),
        user_memory=UserMemoryConfig(mode=LearningMode.AGENTIC),
        learned_knowledge=LearnedKnowledgeConfig(mode=LearningMode.AGENTIC),
    ),
    # Tools
    tools=[
        DuckDuckGoTools(),  # Primary web research
        *build_mcp_tools(env_var="AGNO_ASSIST_MCP_SERVER_URLS", default_urls=[]),  # Optional MCP tools
        DuckDbTools(db_path=duckdb_path),  # Data
    ],
    # Context
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    agno_assist.print_response("Tell me about yourself", stream=True)


__all__ = ["agno_assist", "agno_assist_knowledge"]
