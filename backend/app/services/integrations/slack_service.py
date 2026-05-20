"""
app/services/integrations/slack_service.py

Slack Incoming Webhooks integration.
Sends structured notifications for workflow events.
"""

import httpx

from app.core.config import settings
from app.core.exceptions import IntegrationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class SlackService:
    """Posts messages to Slack via Incoming Webhooks."""

    def __init__(self):
        self.webhook_url = settings.slack_webhook_url

    async def send_message(self, text: str, blocks: list | None = None) -> None:
        """
        Send a plain text or Block Kit message to the configured Slack channel.

        Args:
            text: Fallback text (shown in notifications and when blocks are unavailable).
            blocks: Optional Slack Block Kit payload for rich formatting.
        """
        if not self.webhook_url:
            logger.warning("slack_webhook_not_configured")
            return

        payload: dict = {"text": text}
        if blocks:
            payload["blocks"] = blocks

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(self.webhook_url, json=payload)

        if resp.status_code != 200 or resp.text != "ok":
            raise IntegrationError(
                "Slack",
                f"Webhook failed with status {resp.status_code}: {resp.text}",
            )

        logger.info("slack_message_sent", text_preview=text[:80])

    async def notify_workflow_complete(
        self,
        requirement_title: str,
        requirement_id: str,
        scenario_count: int,
        test_case_count: int,
    ) -> None:
        """Send a rich workflow completion notification."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "✅ QPilot AI — Workflow Complete",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Requirement:*\n{requirement_title}"},
                    {"type": "mrkdwn", "text": f"*ID:*\n`{requirement_id}`"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Scenarios Generated:*\n{scenario_count}"},
                    {"type": "mrkdwn", "text": f"*Test Cases Generated:*\n{test_case_count}"},
                ],
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Powered by *QPilot AI* 🤖 | Review outputs in the dashboard",
                    }
                ],
            },
        ]

        fallback = (
            f"QPilot AI: Workflow complete for '{requirement_title}'. "
            f"{scenario_count} scenarios, {test_case_count} test cases generated."
        )

        await self.send_message(text=fallback, blocks=blocks)

    async def notify_workflow_error(
        self,
        requirement_title: str,
        error_message: str,
    ) -> None:
        """Send an error alert."""
        text = (
            f"❌ QPilot AI Error: Workflow failed for '{requirement_title}'.\n"
            f"Error: {error_message}"
        )
        await self.send_message(text=text)

    async def notify_script_pushed(
        self,
        test_case_title: str,
        github_url: str,
        branch: str,
    ) -> None:
        """Notify that a Playwright script was pushed to GitHub."""
        text = (
            f"🚀 QPilot AI: Automation script pushed to GitHub.\n"
            f"Test: {test_case_title}\n"
            f"Branch: {branch}\n"
            f"Commit: {github_url}"
        )
        await self.send_message(text=text)


# Module-level singleton
slack_service = SlackService()
