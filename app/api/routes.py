import hashlib
import hmac
import time
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from src.agents.slack_agent import slack_agent
from settings import get_settings

router = APIRouter(prefix="/slack", tags=["Slack"])

settings = get_settings()
SLACK_BOT_TOKEN = settings.slack_bot_token
SLACK_SIGNING_SECRET = settings.slack_signing_secret
slack_client = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None
_bot_user_id: str | None = None


def _ensure_slack_configured() -> tuple[WebClient, str]:
    if not slack_client or not SLACK_SIGNING_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Slack integration not configured (set SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET).",
        )
    return slack_client, SLACK_SIGNING_SECRET


def _get_bot_user_id() -> str:
    global _bot_user_id
    client, _ = _ensure_slack_configured()
    if _bot_user_id is None:
        auth_info = client.auth_test()
        user_id = auth_info.get("user_id")
        if not isinstance(user_id, str) or not user_id:
            raise ValueError("Unable to resolve Slack bot user id")
        _bot_user_id = user_id
    return _bot_user_id


def _verify_slack_request(timestamp: str | None, signature: str | None, body: bytes) -> bool:
    _, signing_secret = _ensure_slack_configured()
    if not timestamp or not signature:
        return False

    try:
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False
    except ValueError:
        return False

    basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    computed_signature = "v0=" + hmac.new(
        signing_secret.encode("utf-8"),
        basestring.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature)


def _process_event(event: dict[str, Any]) -> None:
    client, _ = _ensure_slack_configured()
    message = slack_agent.normalize_event(event, bot_user_id=_get_bot_user_id())
    if message is None:
        return
    response_text = slack_agent.respond_to_message(message)
    try:
        client.chat_postMessage(
            channel=message.channel_id,
            text=response_text,
            thread_ts=message.thread_ts,
        )
    except SlackApiError:
        # Keep webhook fast/robust: swallow Slack post errors here.
        return


@router.post("/events")
async def slack_events(request: Request, background_tasks: BackgroundTasks) -> dict[str, Any]:
    raw_body = await request.body()
    payload = await request.json()

    # Handle Slack URL verification before signature checks.
    if payload.get("type") == "url_verification":
        challenge = payload.get("challenge")
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing challenge",
            )
        return {"challenge": challenge}

    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    signature = request.headers.get("X-Slack-Signature")

    if not _verify_slack_request(timestamp=timestamp, signature=signature, body=raw_body):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Slack signature",
        )

    event = payload.get("event")
    if isinstance(event, dict):
        background_tasks.add_task(_process_event, event)

    # Slack only needs a quick ACK.
    return {"ok": True}