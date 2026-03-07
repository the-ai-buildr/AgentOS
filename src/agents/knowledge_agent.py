"""RAG-oriented agent for document-backed knowledge retrieval."""

from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.pgvector import PgVector, SearchType

from src.prompts import load_prompt
from src.models import OpenRouter
from db import db_url, get_postgres_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_postgres_db(contents_table="knowledge_agent_contents")
knowledge = Knowledge(
    name="Knowledge Agent",
    vector_db=PgVector(
        db_url=db_url,
        table_name="knowledge_agent_docs",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
    max_results=10,
    contents_db=agent_db,
)

# ============================================================================
# Create Agent
# ============================================================================
knowledge_agent = Agent(
    id="knowledge-agent",
    name="Knowledge Agent",
    model=OpenRouter.create("openai/gpt-5.4"),
    db=agent_db,
    knowledge=knowledge,
    instructions=load_prompt("knowledge_agent.md"),
    search_knowledge=True,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)


def load_default_documents() -> None:
    """Load default documents into the knowledge base."""
    knowledge.insert(
        name="Agno Introduction",
        url="https://docs.agno.com/introduction.md",
        skip_if_exists=True,
    )
    knowledge.insert(
        name="Agno First Agent",
        url="https://docs.agno.com/first-agent.md",
        skip_if_exists=True,
    )


if __name__ == "__main__":
    load_default_documents()


__all__ = ["knowledge_agent", "knowledge", "load_default_documents"]
