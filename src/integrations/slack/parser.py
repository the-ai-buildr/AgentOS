"""Slack payload parsing and normalization utilities."""

from dataclasses import dataclass
import re
from typing import Any

_URL_RE = re.compile(r"https?://\S+")


@dataclass(slots=True)
class SlackMessage:
    """Slack-agnostic message payload used by downstream workflows."""

    source: str
    user_id: str
    channel_id: str
    thread_ts: str
    message_ts: str
    text: str
    mentioned: bool
    is_dm: bool
    is_command: bool
    files: list[dict[str, Any]]
    links: list[str]
    raw_event: dict[str, Any]


def normalize_slack_event(event: dict[str, Any], *, bot_user_id: str) -> SlackMessage | None:
    """Normalize Slack event payload to a stable internal shape."""
    event_type = str(event.get("type") or "")
    if event_type not in {"app_mention", "message"}:
        return None
    if event.get("bot_id"):
        return None
    if str(event.get("subtype") or "") == "bot_message":
        return None

    user_id = str(event.get("user") or "")
    channel_id = str(event.get("channel") or "")
    message_ts = str(event.get("ts") or "")
    thread_ts = str(event.get("thread_ts") or message_ts)
    raw_text = str(event.get("text") or "")
    if not user_id or not channel_id or not message_ts:
        return None

    mention_token = f"<@{bot_user_id}>"
    mentioned = mention_token in raw_text or event_type == "app_mention"
    is_dm = str(event.get("channel_type") or "") == "im"
    if not mentioned and not is_dm:
        return None

    normalized_text = raw_text.replace(mention_token, "").strip()
    files = event.get("files")
    file_list = files if isinstance(files, list) else []
    links = _URL_RE.findall(normalized_text)

    return SlackMessage(
        source="slack",
        user_id=user_id,
        channel_id=channel_id,
        thread_ts=thread_ts,
        message_ts=message_ts,
        text=normalized_text,
        mentioned=mentioned,
        is_dm=is_dm,
        is_command=normalized_text.startswith("/"),
        files=[f for f in file_list if isinstance(f, dict)],
        links=links,
        raw_event=event,
    )


__all__ = ["SlackMessage", "normalize_slack_event"]
