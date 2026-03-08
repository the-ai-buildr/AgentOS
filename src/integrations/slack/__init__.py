"""Slack integration primitives (parser/formatter/webhook)."""

from .formatter import format_slack_response
from .parser import SlackMessage, normalize_slack_event
from .webhook import post_slack_webhook

__all__ = ["SlackMessage", "format_slack_response", "normalize_slack_event", "post_slack_webhook"]
