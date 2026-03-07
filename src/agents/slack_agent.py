"""Optional Slack-facing conversational agent."""

from agno.agent import Agent
from src.models import OpenRouter
from src.prompts import load_prompt

slack_agent = Agent(
    name="Slack Agent",
    model=OpenRouter.create("openai/gpt-5.4"),
    instructions=load_prompt("slack_agent.md"),
    add_history_to_context=True,
    num_history_runs=3,
    add_datetime_to_context=True,
)

if __name__ == "__main__":
    slack_agent.print_response("Tell me about yourself", stream=True)


__all__ = ["slack_agent"]