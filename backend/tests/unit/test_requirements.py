"""
tests/unit/test_requirements.py

Tests for requirement CRUD endpoints.
AI service is mocked so tests don't need OpenAI credentials.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient


MOCK_ANALYSIS = {
    "main_functionality": "User authentication via email and password",
    "testing_areas": ["Login form validation", "Session management"],
    "potential_risks": ["SQL injection", "Brute force attacks"],
    "validation_points": ["Email format validation", "Password strength"],
    "edge_cases": ["Empty fields", "Special characters in password"],
    "recommended_scenario_count": 6,
}


class TestCreateRequirement:
    @patch("app.api.v1.endpoints.requirements.ai_service.analyze_requirement",
           new_callable=AsyncMock, return_value=MOCK_ANALYSIS)
    async def test_create_success(self, mock_ai, auth_client: AsyncClient):
        resp = await auth_client.post("/api/v1/requirements", json={
            "title": "User Login with Email and Password",
            "description": "As a registered user, I want to log in using my email and password so that I can access my account dashboard.",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["title"] == "User Login with Email and Password"
        assert data["data"]["status"] in ("analyzed", "failed")
        mock_ai.assert_called_once()

    async def test_create_unauthenticated(self, client: AsyncClient):
        resp = await client.post("/api/v1/requirements", json={
            "title": "Some requirement",
            "description": "Some description that is long enough to pass validation checks",
        })
        assert resp.status_code == 401

    async def test_create_title_too_short(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/v1/requirements", json={
            "title": "Hi",  # less than 5 chars
            "description": "A valid long description for this test case",
        })
        assert resp.status_code == 422

    async def test_create_description_too_short(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/v1/requirements", json={
            "title": "Valid Title Here",
            "description": "Short",  # less than 20 chars
        })
        assert resp.status_code == 422


class TestListRequirements:
    @patch("app.api.v1.endpoints.requirements.ai_service.analyze_requirement",
           new_callable=AsyncMock, return_value=MOCK_ANALYSIS)
    async def test_list_empty(self, mock_ai, auth_client: AsyncClient):
        resp = await auth_client.get("/api/v1/requirements")
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] == 0

    @patch("app.api.v1.endpoints.requirements.ai_service.analyze_requirement",
           new_callable=AsyncMock, return_value=MOCK_ANALYSIS)
    async def test_list_with_items(self, mock_ai, auth_client: AsyncClient):
        # Create two requirements
        for i in range(2):
            await auth_client.post("/api/v1/requirements", json={
                "title": f"Requirement {i+1} Title Here",
                "description": "Detailed description for the requirement that passes minimum length validation",
            })

        resp = await auth_client.get("/api/v1/requirements")
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] == 2

    async def test_list_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/requirements")
        assert resp.status_code == 401


class TestGetRequirement:
    @patch("app.api.v1.endpoints.requirements.ai_service.analyze_requirement",
           new_callable=AsyncMock, return_value=MOCK_ANALYSIS)
    async def test_get_existing(self, mock_ai, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/v1/requirements", json={
            "title": "Requirement to Fetch by ID",
            "description": "Detailed enough description to pass the minimum validation length requirement",
        })
        req_id = create_resp.json()["data"]["id"]

        resp = await auth_client.get(f"/api/v1/requirements/{req_id}")
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == req_id

    async def test_get_nonexistent(self, auth_client: AsyncClient):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await auth_client.get(f"/api/v1/requirements/{fake_id}")
        assert resp.status_code == 404
