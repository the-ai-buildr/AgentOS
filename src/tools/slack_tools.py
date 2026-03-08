"""Slack-specific tool helpers for agent usage."""

from settings import get_settings
from src.integrations.slack.webhook import post_slack_webhook


def send_workspace_webhook_update(text: str) -> str:
    """
    Send an outbound status message to the configured AgentOS channel webhook.

    Returns a clear success/failure message for agent tool-calling loops.
    """
    webhook_url = get_settings().slack_workspace_webhook_url
    if not webhook_url:
        return "AgentOS channel webhook is not configured. Set SLACK_WORKSPACE_WEBHOOK_URL."

    clean_text = (text or "").strip()
    if not clean_text:
        return "No message sent. 'text' must be non-empty."

    ok = post_slack_webhook(webhook_url, text=clean_text)
    return "AgentOS channel webhook message sent." if ok else "AgentOS channel webhook send failed."


__all__ = ["send_workspace_webhook_update"]
