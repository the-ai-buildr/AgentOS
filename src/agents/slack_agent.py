"""Slack-facing coordinator that routes requests to core workflows."""

from dataclasses import dataclass, field
from typing import Any

from src.agents.agno_assist import agno_assist
from src.agents.knowledge_agent import knowledge_agent
from src.integrations.slack.formatter import format_slack_response
from src.integrations.slack.parser import SlackMessage, normalize_slack_event
from src.integrations.slack.webhook import post_slack_webhook
from src.workflows.route_slack_message import route_slack_message
from settings import get_settings


@dataclass(slots=True)
class SlackAgentCoordinator:
    """Thin Slack channel coordinator over core agents/workflows."""

    chat_agent: Any = field(default_factory=lambda: agno_assist)
    research_agent: Any = field(default_factory=lambda: knowledge_agent)
    task_agent: Any = field(default_factory=lambda: agno_assist)
    note_agent: Any = field(default_factory=lambda: agno_assist)
    workspace_channel_id: str | None = field(default_factory=lambda: get_settings().slack_workspace_channel_id)
    workspace_webhook_url: str | None = field(default_factory=lambda: get_settings().slack_workspace_webhook_url)
    _workspace_agent: Any | None = field(default=None, init=False, repr=False)

    def normalize_event(self, event: dict[str, Any], *, bot_user_id: str) -> SlackMessage | None:
        """Convert raw Slack event payloads into a Slack-agnostic message shape."""
        return normalize_slack_event(event, bot_user_id=bot_user_id)

    def respond_to_message(self, message: SlackMessage) -> str:
        """Route a normalized Slack message to the best-matching workflow."""
        chat_agent = self.chat_agent
        research_agent = self.research_agent
        task_agent = self.task_agent
        note_agent = self.note_agent

        if self.workspace_channel_id and message.channel_id == self.workspace_channel_id:
            workspace_agent = self._get_workspace_agent()
            chat_agent = workspace_agent
            research_agent = workspace_agent
            task_agent = workspace_agent
            note_agent = workspace_agent

        route_result = route_slack_message(
            message,
            chat_agent=chat_agent,
            research_agent=research_agent,
            task_agent=task_agent,
            note_agent=note_agent,
        )
        return format_slack_response(route_result.response_text, intent=route_result.intent)

    def _get_workspace_agent(self) -> Any:
        """Lazily load the workspace specialist only when configured/needed."""
        if self._workspace_agent is None:
            from src.teams.neo_orchestrator import communication_agent

            self._workspace_agent = communication_agent
        return self._workspace_agent

    def notify_workspace(self, text: str, *, blocks: list[dict[str, Any]] | None = None) -> bool:
        """
        Send one-way outbound updates to Slack #workspace via Incoming Webhook.

        Returns True when the webhook call succeeds.
        """
        if not self.workspace_webhook_url:
            return False
        if not text.strip():
            return False
        return post_slack_webhook(self.workspace_webhook_url, text=text, blocks=blocks)

    def run(self, prompt: str) -> str:
        """Backwards-compatible entrypoint used by direct callers/tests."""
        synthetic = SlackMessage(
            source="slack",
            user_id="local-user",
            channel_id="local-channel",
            thread_ts="local-thread",
            message_ts="local-message",
            text=prompt,
            mentioned=True,
            is_dm=True,
            is_command=prompt.strip().startswith("/"),
            files=[],
            links=[],
            raw_event={},
        )
        return self.respond_to_message(synthetic)


slack_agent = SlackAgentCoordinator()

__all__ = ["SlackAgentCoordinator", "slack_agent"]