from agno.agent import Agent
from src.models import OpenRouter
from db import get_postgres_db
from src.tools.mcp_tools import build_mcp_tools
from src.prompts import load_prompt

# ============================================================================
# Setup
# ============================================================================
agent_db = get_postgres_db()

# ============================================================================
# Create Agent
# ============================================================================
mcp_agent = Agent(
    id="mcp-agent",
    name="MCP Agent",
    model=OpenRouter.create("openai/gpt-5.4"),
    db=agent_db,
    tools=build_mcp_tools(default_urls=["https://docs.agno.com/mcp"]),
    instructions=load_prompt("mcp_agent.md"),
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    mcp_agent.print_response("What tools do you have access to?", stream=True)
