from agno.agent import Agent

from src.prompts import load_prompt
from db import get_postgres_db
from models import OpenRouter


research_agent = Agent(
    id="research-agent",
    name="Research Agent",
    model=OpenRouter.create(model_type="gemini-flash"),
    db=get_postgres_db(),
    instructions=load_prompt("research_agent.md"),
    add_history_to_context=True,
    num_history_runs=5,
    add_datetime_to_context=True,
    markdown=True,
)


if __name__ == "__main__":
    research_agent.print_response("Explain your research and synthesis workflow.", stream=True)
