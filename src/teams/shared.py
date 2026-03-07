"""Shared team dependencies: memory store, skills, and local data paths."""

from os import getenv
from pathlib import Path

from agno.learn import (
    LearnedKnowledgeConfig,
    LearningMachine,
    LearningMode,
    UserMemoryConfig,
    UserProfileConfig,
)
from agno.skills import LocalSkills, Skills

from db import get_postgres_db
from src.models import OpenRouter

db = get_postgres_db()
data_dir = Path(getenv("DATA_DIR", "/data"))
data_dir.mkdir(parents=True, exist_ok=True)
duckdb_path = str(data_dir / "neo_team.db")

skills_dir = Path(__file__).resolve().parent.parent / "skills"
neo_skills = Skills(loaders=[LocalSkills(str(skills_dir))])

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


__all__ = ["db", "duckdb_path", "neo_skills", "neo_team_learning_store"]
