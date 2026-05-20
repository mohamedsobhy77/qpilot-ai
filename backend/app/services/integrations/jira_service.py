"""
app/services/integrations/jira_service.py

Jira REST API v3 integration.
Creates issues (Tasks, Bugs, Stories) from QA outputs.
"""

import base64

import httpx

from app.core.config import settings
from app.core.exceptions import IntegrationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class JiraService:
    """Wraps Jira REST API v3 for issue creation and management."""

    def __init__(self):
        # Basic auth: base64(email:api_token)
        credentials = f"{settings.jira_email}:{settings.jira_api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.base_url = settings.jira_base_url.rstrip("/")
        self.project_key = settings.jira_project_key

    async def create_issue(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
        labels: list[str] | None = None,
    ) -> dict:
        """
        Create a Jira issue.

        Returns:
            dict with jira_ticket_key and jira_ticket_url
        """
        url = f"{self.base_url}/rest/api/3/issue"

        # Jira's Atlassian Document Format (ADF) for description
        adf_description = self._to_adf(description)

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": adf_description,
                "issuetype": {"name": issue_type},
                "priority": {"name": priority},
                "labels": labels or ["qpilot-ai", "automated"],
            }
        }

        async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
            resp = await client.post(url, json=payload)

        if resp.status_code not in (200, 201):
            raise IntegrationError(
                "Jira",
                f"Issue creation failed with status {resp.status_code}: {resp.text[:300]}",
            )

        data = resp.json()
        ticket_key = data["key"]
        ticket_url = f"{self.base_url}/browse/{ticket_key}"

        logger.info(
            "jira_issue_created",
            ticket_key=ticket_key,
            issue_type=issue_type,
            summary=summary[:80],
        )

        return {
            "jira_ticket_key": ticket_key,
            "jira_ticket_url": ticket_url,
        }

    @staticmethod
    def _to_adf(text: str) -> dict:
        """
        Convert plain text to Atlassian Document Format (ADF).
        Jira API v3 requires ADF instead of plain text for description fields.
        """
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        content = []
        for para in paragraphs:
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": para}],
            })

        if not content:
            content = [{"type": "paragraph", "content": [{"type": "text", "text": text}]}]

        return {
            "type": "doc",
            "version": 1,
            "content": content,
        }


# Module-level singleton
jira_service = JiraService()
