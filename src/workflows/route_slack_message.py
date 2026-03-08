"""Intent routing workflow for normalized Slack messages."""

from dataclasses import dataclass
import re
from typing import Any

from src.integrations.slack.parser import SlackMessage


_NOTE_PATTERNS = (
    r"\bnote\b",
    r"\bsave this\b",
    r"\bremember this\b",
    r"\bbookmark\b",
    r"\bcapture\b",
)
_TASK_PATTERNS = (
    r"\bcreate (a )?task\b",
    r"\badd (a )?task\b",
    r"\bto[- ]?do\b",
    r"\bproject\b",
    r"\baction item\b",
)
_RESEARCH_PATTERNS = (
    r"\bresearch\b",
    r"\binvestigate\b",
    r"\blook up\b",
    r"\bfind sources\b",
    r"\bdeep dive\b",
)
_SUMMARIZE_PATTERNS = (
    r"\bsummarize\b.*\bthread\b",
    r"\bsummary\b.*\bthread\b",
    r"\btl;dr\b.*\bthread\b",
)


@dataclass(slots=True)
class SlackRouteResult:
    """Workflow output returned to Slack channel formatting layer."""

    intent: str
    response_text: str


def _run_agent_text(agent: Any, prompt: str) -> str:
    """Call an Agno agent and normalize its response payload to text."""
    if not prompt:
        return "How can I help?"
    result = agent.run(prompt)
    if isinstance(result, str):
        return result.strip() or "How can I help?"
    content = getattr(result, "content", None)
    if isinstance(content, str):
        return content.strip() or "How can I help?"
    return str(result).strip() or "How can I help?"


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def detect_intent(message: SlackMessage) -> str:
    """Rule-based intent classifier for Slack MVP routing."""
    text = message.text.strip()
    if not text:
        return "chat"
    if message.is_command:
        return "command"
    if _matches_any(text, _SUMMARIZE_PATTERNS):
        return "summarize"
    if _matches_any(text, _NOTE_PATTERNS):
        return "note"
    if _matches_any(text, _TASK_PATTERNS):
        return "task"
    if _matches_any(text, _RESEARCH_PATTERNS):
        return "research"
    return "chat"


def route_slack_message(
    message: SlackMessage,
    *,
    chat_agent: Any,
    research_agent: Any,
    task_agent: Any,
    note_agent: Any,
 ) -> SlackRouteResult:
    """Route a normalized Slack message to the right core workflow."""
    intent = detect_intent(message)
    if intent == "note":
        response = _run_agent_text(
            note_agent,
            (
                "Capture the following as a durable note. "
                "Respond with: (1) short confirmation, (2) extracted bullets, (3) suggested tags.\n\n"
                f"{message.text}"
            ),
        )
        return SlackRouteResult(intent=intent, response_text=response)
    if intent == "task":
        response = _run_agent_text(
            task_agent,
            (
                "Convert this into actionable tasks. "
                "Respond with concise task bullets that include owner placeholder, due date placeholder, and next action.\n\n"
                f"{message.text}"
            ),
        )
        return SlackRouteResult(intent=intent, response_text=response)
    if intent == "research":
        response = _run_agent_text(
            research_agent,
            f"Research this request and return concise findings with source links:\n\n{message.text}",
        )
        return SlackRouteResult(intent=intent, response_text=response)
    if intent == "summarize":
        response = _run_agent_text(
            chat_agent,
            (
                "Provide a concise thread-style summary in bullets. "
                "If source context is limited, state assumptions clearly.\n\n"
                f"{message.text}"
            ),
        )
        return SlackRouteResult(intent=intent, response_text=response)
    if intent == "command":
        response = _run_agent_text(chat_agent, f"Interpret this Slack command and respond succinctly:\n\n{message.text}")
        return SlackRouteResult(intent=intent, response_text=response)

    response = _run_agent_text(chat_agent, message.text)
    return SlackRouteResult(intent=intent, response_text=response)


__all__ = ["SlackRouteResult", "detect_intent", "route_slack_message"]
