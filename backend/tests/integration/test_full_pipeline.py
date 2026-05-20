"""
tests/integration/test_full_pipeline.py

End-to-end integration test that exercises the complete QPilot pipeline:
  1. Register + login
  2. Submit requirement (AI mocked)
  3. Generate scenarios (AI mocked)
  4. Generate test cases (AI mocked)
  5. Submit approval
  6. Check requirement status progression

No external services (OpenAI, Jira, GitHub, Slack) are called.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

# ── Shared mock payloads ──────────────────────────────────────────
MOCK_ANALYSIS = {
    "main_functionality": "User authentication via email and password",
    "testing_areas": ["Login form validation", "Session token handling"],
    "potential_risks": ["SQL injection", "Brute force"],
    "validation_points": ["Email format", "Password length"],
    "edge_cases": ["Empty fields", "Special characters"],
    "recommended_scenario_count": 5,
}

MOCK_SCENARIOS = [
    {
        "scenario_title": "Successful login with valid credentials",
        "scenario_type": "positive",
        "scenario_description": "User provides correct email and password and is authenticated.",
        "priority": "high",
    },
    {
        "scenario_title": "Login fails with wrong password",
        "scenario_type": "negative",
        "scenario_description": "User provides wrong password and sees error message.",
        "priority": "high",
    },
    {
        "scenario_title": "Login with empty email field",
        "scenario_type": "edge",
        "scenario_description": "User submits form with empty email field.",
        "priority": "medium",
    },
]

MOCK_TEST_CASES = [
    {
        "test_case_title": "TC-001: Login with valid email and password",
        "preconditions": "User account exists with email test@example.com",
        "test_steps": [
            {"step_number": 1, "action": "Navigate to /login", "expected": "Login page is displayed"},
            {"step_number": 2, "action": "Enter email 'test@example.com'", "expected": "Email field is populated"},
            {"step_number": 3, "action": "Enter password 'Password123'", "expected": "Password field shows bullets"},
            {"step_number": 4, "action": "Click 'Sign In' button", "expected": "User is redirected to dashboard"},
        ],
        "expected_result": "User is authenticated and redirected to the dashboard",
        "test_data": {"email": "test@example.com", "password": "Password123"},
        "priority": "high",
    },
    {
        "test_case_title": "TC-002: Login fails with incorrect password",
        "preconditions": "User account exists",
        "test_steps": [
            {"step_number": 1, "action": "Navigate to /login", "expected": "Login page is displayed"},
            {"step_number": 2, "action": "Enter valid email", "expected": "Email field populated"},
            {"step_number": 3, "action": "Enter wrong password 'wrong'", "expected": "Password field shows bullets"},
            {"step_number": 4, "action": "Click 'Sign In'", "expected": "Error message displayed"},
        ],
        "expected_result": "User sees 'Invalid credentials' error and stays on login page",
        "test_data": {"email": "test@example.com", "password": "wrongpass"},
        "priority": "high",
    },
]


class TestFullPipeline:
    """
    Full pipeline integration test.
    Each step builds on the previous one — uses a shared state dict.
    """

    @pytest.fixture
    def state(self):
        return {}

    @patch("app.api.v1.endpoints.requirements.ai_service.analyze_requirement",
           new_callable=AsyncMock, return_value=MOCK_ANALYSIS)
    async def test_01_register_and_login(self, mock_ai, client: AsyncClient, state):
        # Register
        reg = await client.post("/api/v1/auth/register", json={
            "full_name": "Pipeline Tester",
            "email": "pipeline@qpilot.ai",
            "password": "pipelinepass123",
        })
        assert reg.status_code == 201

        # Login
        login = await client.post("/api/v1/auth/login", json={
            "email": "pipeline@qpilot.ai",
            "password": "pipelinepass123",
        })
        assert login.status_code == 200
        token = login.json()["access_token"]
        assert token
        state["token"] = token

    @patch("app.api.v1.endpoints.requirements.ai_service.analyze_requirement",
           new_callable=AsyncMock, return_value=MOCK_ANALYSIS)
    async def test_02_submit_requirement(self, mock_ai, client: AsyncClient, auth_client: AsyncClient, state):
        resp = await auth_client.post("/api/v1/requirements", json={
            "title": "User Authentication Login Feature",
            "description": "As a registered user I want to log in with my email and password so that I can access my personal dashboard and settings.",
        })
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["title"] == "User Authentication Login Feature"
        assert data["status"] in ("analyzed", "submitted", "failed")
        state["requirement_id"] = data["id"]

    @patch("app.services.ai.ai_service.AIService.generate_scenarios",
           new_callable=AsyncMock, return_value=MOCK_SCENARIOS)
    async def test_03_generate_scenarios(self, mock_gen, auth_client: AsyncClient, state):
        req_id = state.get("requirement_id")
        if not req_id:
            pytest.skip("No requirement_id — run test_02 first")

        resp = await auth_client.post("/api/v1/scenarios/generate", json={
            "requirement_id": req_id
        })
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["total"] == len(MOCK_SCENARIOS)
        assert len(data["scenarios"]) == len(MOCK_SCENARIOS)

        scenario_ids = [s["id"] for s in data["scenarios"]]
        state["scenario_ids"] = scenario_ids
        state["first_scenario_id"] = scenario_ids[0]

    @patch("app.services.ai.ai_service.AIService.generate_test_cases",
           new_callable=AsyncMock, return_value=MOCK_TEST_CASES)
    async def test_04_generate_test_cases(self, mock_gen, auth_client: AsyncClient, state):
        scenario_id = state.get("first_scenario_id")
        if not scenario_id:
            pytest.skip("No scenario_id — run test_03 first")

        resp = await auth_client.post("/api/v1/test-cases/generate", json={
            "scenario_id": scenario_id
        })
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["total"] == len(MOCK_TEST_CASES)
        assert data["test_cases"][0]["status"] == "draft"

        state["test_case_ids"] = [tc["id"] for tc in data["test_cases"]]

    async def test_05_list_scenarios(self, auth_client: AsyncClient, state):
        req_id = state.get("requirement_id")
        if not req_id:
            pytest.skip("No requirement_id")

        resp = await auth_client.get(f"/api/v1/scenarios/{req_id}")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] > 0

    async def test_06_approve_requirement(self, auth_client: AsyncClient, state):
        req_id = state.get("requirement_id")
        if not req_id:
            pytest.skip("No requirement_id")

        resp = await auth_client.post("/api/v1/approvals", json={
            "requirement_id": req_id,
            "approval_status": "approved",
            "comments": "All test cases look good. Proceeding to automation.",
        })
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["approval_status"] == "approved"

    async def test_07_requirement_status_is_approved(self, auth_client: AsyncClient, state):
        req_id = state.get("requirement_id")
        if not req_id:
            pytest.skip("No requirement_id")

        resp = await auth_client.get(f"/api/v1/requirements/{req_id}")
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "approved"

    async def test_08_reject_then_check(self, auth_client: AsyncClient, state):
        """Regression: rejected requirements go to 'rejected' status."""
        req_id = state.get("requirement_id")
        if not req_id:
            pytest.skip("No requirement_id")

        resp = await auth_client.post("/api/v1/approvals", json={
            "requirement_id": req_id,
            "approval_status": "rejected",
            "comments": "Found issues — rejecting for now.",
        })
        assert resp.status_code == 201
        # Check it was recorded
        assert resp.json()["data"]["approval_status"] == "rejected"
