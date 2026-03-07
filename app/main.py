from os import getenv
from pathlib import Path

from agno.os import AgentOS

from src.agents.knowledge_agent import knowledge_agent
from src.agents.mcp_agent import mcp_agent
from src.teams.neo_team import neo_team
from src.agents.agno_assist import agno_assist, agno_assist_knowledge
from agno.os.interfaces.slack import Slack
from src.agents.slack_agent import slack_agent
from db import get_postgres_db
import os


# ============================================================================
# Create AgentOS
# ============================================================================
agent_os = AgentOS(
    name="The Ai Buildr - AgentOS",
    tracing=True,
    db=get_postgres_db(),
    agents=[ agno_assist, knowledge_agent, mcp_agent ],
    teams=[ neo_team ],
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(
        app="app.main:app",
        interfaces=[Slack(agent=slack_agent)],
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
