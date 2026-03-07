"""Research and analysis sub-team with evidence synthesis roles."""

from agno.agent import Agent
from agno.team import Team
from agno.team.mode import TeamMode

from src.models import OpenRouter
from src.prompts import load_prompt

deep_researcher = Agent(
    id="neo-deep-researcher",
    name="Deep Researcher",
    role="Perform deep web-grounded research with citations using Perplexity.",
    model=OpenRouter.create(model_type="perplexity-reasoning"),
    instructions=load_prompt("deep_researcher.md"),
    add_datetime_to_context=True,
    markdown=True,
)

research_analyst = Agent(
    id="neo-research-analyst",
    name="Research Analyst",
    role="Evaluate evidence quality, grade sources, and produce structured analysis.",
    model=OpenRouter.create(model_type="claude-sonnet"),
    instructions=load_prompt("research_analyst.md"),
    add_datetime_to_context=True,
    markdown=True,
)

research_team = Team(
    id="neo-research-team",
    name="Research Team",
    role=(
        "Evidence-based discovery, deep research, and synthesis. Produces structured "
        "findings reports with source grading and recommendations."
    ),
    mode=TeamMode.coordinate,
    model=OpenRouter.create(model_type="claude-sonnet"),
    members=[deep_researcher, research_analyst],
    instructions=load_prompt("research_lead.md"),
    show_members_responses=True,
    markdown=True,
)


__all__ = ["research_team", "deep_researcher", "research_analyst"]
