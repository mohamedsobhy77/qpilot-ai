"""
app/services/integrations/github_service.py

GitHub REST API integration.
Pushes generated Playwright scripts to a GitHub repository.
"""

import base64
from datetime import datetime

import httpx

from app.core.config import settings
from app.core.exceptions import IntegrationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class GitHubService:
    """Wraps GitHub REST API for automation script commits."""

    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.owner = settings.github_owner
        self.repo = settings.github_repo

    async def push_script(
        self,
        filename: str,
        content: str,
        branch: str | None = None,
    ) -> dict:
        """
        Push a script file to GitHub.

        Steps:
        1. Get the SHA of the default branch HEAD
        2. Create a new feature branch
        3. Commit the file to that branch

        Returns:
            dict with commit_url and branch name
        """
        if not branch:
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            branch = f"qpilot/automation/{timestamp}"

        async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
            # Step 1: Get default branch SHA
            sha = await self._get_default_branch_sha(client)

            # Step 2: Create branch
            await self._create_branch(client, branch, sha)

            # Step 3: Commit file
            commit_url = await self._commit_file(client, filename, content, branch)

        logger.info(
            "github_push_success",
            filename=filename,
            branch=branch,
            commit_url=commit_url,
        )

        return {"commit_url": commit_url, "branch": branch}

    async def _get_default_branch_sha(self, client: httpx.AsyncClient) -> str:
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}"
        resp = await client.get(url)
        self._raise_for_status(resp, "get repository info")

        default_branch = resp.json()["default_branch"]

        ref_url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/git/ref/heads/{default_branch}"
        ref_resp = await client.get(ref_url)
        self._raise_for_status(ref_resp, "get branch SHA")

        return ref_resp.json()["object"]["sha"]

    async def _create_branch(
        self, client: httpx.AsyncClient, branch: str, sha: str
    ) -> None:
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/git/refs"
        payload = {"ref": f"refs/heads/{branch}", "sha": sha}
        resp = await client.post(url, json=payload)

        # 422 means branch already exists — treat as non-fatal
        if resp.status_code not in (201, 422):
            self._raise_for_status(resp, "create branch")

    async def _commit_file(
        self,
        client: httpx.AsyncClient,
        filename: str,
        content: str,
        branch: str,
    ) -> str:
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/contents/tests/{filename}"
        encoded = base64.b64encode(content.encode()).decode()

        payload = {
            "message": f"feat(automation): add {filename} [QPilot AI]",
            "content": encoded,
            "branch": branch,
        }
        resp = await client.put(url, json=payload)
        self._raise_for_status(resp, "commit file")

        return resp.json()["commit"]["html_url"]

    @staticmethod
    def _raise_for_status(response: httpx.Response, operation: str) -> None:
        if response.status_code >= 400:
            raise IntegrationError(
                "GitHub",
                f"'{operation}' failed with status {response.status_code}: {response.text[:200]}",
            )


# Module-level singleton
github_service = GitHubService()
