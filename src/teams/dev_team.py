"""Developer execution sub-team and members."""

from agno.agent import Agent
from agno.team import Team
from agno.team.mode import TeamMode

from src.models import OpenRouter
from src.prompts import load_prompt

dev_implementer = Agent(
    id="neo-dev-implementer",
    name="Dev Implementer",
    role="Build solutions and implement tasks according to the approach set by the Dev Lead.",
    model=OpenRouter.create(model_type="claude-sonnet"),
    instructions=load_prompt("dev_implementer.md"),
    add_datetime_to_context=True,
    markdown=True,
)

dev_reviewer = Agent(
    id="neo-dev-reviewer",
    name="Dev Reviewer",
    role="Validate implementation output against acceptance criteria and report pass/fail.",
    model=OpenRouter.create(model_type="grok"),
    instructions=load_prompt("dev_reviewer.md"),
    add_datetime_to_context=True,
    markdown=True,
)

dev_team = Team(
    id="neo-dev-team",
    name="Dev Team",
    role=(
        "Implementation, debugging, and technical problem-solving. Receives defined "
        "tasks with acceptance criteria and delivers verified results."
    ),
    mode=TeamMode.coordinate,
    model=OpenRouter.create(model_type="claude-sonnet"),
    members=[dev_implementer, dev_reviewer],
    instructions=load_prompt("dev_lead.md"),
    show_members_responses=True,
    markdown=True,
)


__all__ = ["dev_team", "dev_implementer", "dev_reviewer"]
