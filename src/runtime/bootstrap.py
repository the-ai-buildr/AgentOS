from pathlib import Path

from agno.os import AgentOS
from agno.scheduler import ScheduleManager

from db import get_postgres_db
from settings import Settings, get_settings


def build_agent_os(settings: Settings | None = None) -> AgentOS:
    """Build and configure the AgentOS runtime."""
    cfg = settings or get_settings()

    db = get_postgres_db()

    # Import runtime components lazily so this module is a clean composition root.
    from src.agents.agno_assist import agno_assist
    from src.agents.knowledge_agent import knowledge_agent
    from src.schedules.pulse_schedule import register_pulse_schedule
    from src.teams.neo_orchestrator import neo_team, pulse_agent

    mgr = ScheduleManager(db)
    register_pulse_schedule(mgr)

    repo_root = Path(__file__).resolve().parents[2]
    config_path = repo_root / "app" / "config.yaml"

    return AgentOS(
        name=cfg.agentos_name,
        tracing=cfg.tracing,
        db=db,
        agents=[agno_assist, knowledge_agent, pulse_agent],
        teams=[neo_team],
        config=str(config_path),
        scheduler=cfg.scheduler_enabled,
        scheduler_poll_interval=cfg.scheduler_poll_interval,
    )
