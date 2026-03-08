"""Slack Incoming Webhook helpers."""

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def post_slack_webhook(
    webhook_url: str,
    *,
    text: str,
    blocks: list[dict[str, Any]] | None = None,
    timeout: float = 10.0,
) -> bool:
    """Post a message to Slack using an incoming webhook URL."""
    payload: dict[str, Any] = {"text": text}
    if blocks:
        payload["blocks"] = blocks

    body = json.dumps(payload).encode("utf-8")
    request = Request(
        webhook_url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            status_code = getattr(response, "status", 200)
            return 200 <= int(status_code) < 300
    except (HTTPError, URLError, TimeoutError):
        return False


__all__ = ["post_slack_webhook"]
