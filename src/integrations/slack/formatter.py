"""Slack response formatting helpers."""

from textwrap import shorten

_MAX_SLACK_TEXT_CHARS = 3000


def format_slack_response(text: str, *, intent: str) -> str:
    """
    Return a concise Slack-friendly response string.

    Slack supports larger payloads, but keeping responses compact improves
    readability in busy channels.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return "How can I help?"

    if len(cleaned) > _MAX_SLACK_TEXT_CHARS:
        cleaned = shorten(cleaned, width=_MAX_SLACK_TEXT_CHARS, placeholder=" ...")

    if intent in {"task", "note", "research", "summarize"} and not cleaned.startswith("•"):
        return cleaned
    return cleaned


__all__ = ["format_slack_response"]
