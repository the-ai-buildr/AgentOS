from os import getenv
from pathlib import Path

from agno.os import AgentOS
from agno.scheduler import ScheduleManager

from src.agents.knowledge_agent import knowledge_agent
from src.teams.neo_team import neo_team, pulse_agent
from src.agents.agno_assist import agno_assist, agno_assist_knowledge
from src.schedules.pulse_schedule import register_pulse_schedule
from agno.os.interfaces.slack import Slack
from src.agents.slack_agent import slack_agent
from db import get_postgres_db


# ============================================================================
# Database
# ============================================================================

db = get_postgres_db()

# ============================================================================
# Scheduler — register all schedules
# ============================================================================

mgr = ScheduleManager(db)
register_pulse_schedule(mgr)

# ============================================================================
# Create AgentOS
# ============================================================================

agent_os = AgentOS(
    name="The Ai Buildr - AgentOS",
    tracing=True,
    db=db,
    agents=[agno_assist, knowledge_agent, pulse_agent],
    teams=[neo_team],
    config=str(Path(__file__).parent / "config.yaml"),
    scheduler=True,
    scheduler_poll_interval=15,
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(
        app="app.main:app",
        # interfaces=[Slack(agent=slack_agent)],
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
