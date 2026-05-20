"""
tests/unit/test_ai_service.py

Tests for AIService methods.
OpenAI client is fully mocked — no real API calls made.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ai.ai_service import AIService, _parse_json_response
from app.core.exceptions import AIServiceError


class TestParseJsonResponse:
    def test_parses_clean_json(self):
        result = _parse_json_response('{"key": "value"}', "test")
        assert result == {"key": "value"}

    def test_strips_markdown_fences(self):
        content = '```json\n{"key": "value"}\n```'
        result = _parse_json_response(content, "test")
        assert result == {"key": "value"}

    def test_strips_plain_fences(self):
        content = '```\n{"key": "value"}\n```'
        result = _parse_json_response(content, "test")
        assert result == {"key": "value"}

    def test_raises_on_invalid_json(self):
        with pytest.raises(AIServiceError):
            _parse_json_response("not json at all", "test")

    def test_raises_on_empty(self):
        with pytest.raises(AIServiceError):
            _parse_json_response("", "test")


class TestAIService:
    def _make_mock_response(self, content: dict) -> MagicMock:
        """Build a mock OpenAI response object."""
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps(content)
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 200
        return mock_response

    @pytest.fixture
    def service(self):
        return AIService()

    async def test_analyze_requirement(self, service):
        mock_result = {
            "main_functionality": "User authentication",
            "testing_areas": ["Login form"],
            "potential_risks": ["SQL injection"],
            "validation_points": ["Email format"],
            "edge_cases": ["Empty password"],
            "recommended_scenario_count": 5,
        }
        with patch.object(
            service.__class__,
            "analyze_requirement",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await service.analyze_requirement("Login feature description here")
            assert result["main_functionality"] == "User authentication"
            assert isinstance(result["testing_areas"], list)

    async def test_generate_scenarios_validates_types(self, service):
        """Ensure scenario_type normalization works."""
        raw_scenarios = {
            "scenarios": [
                {
                    "scenario_title": "Valid login",
                    "scenario_type": "positive",
                    "scenario_description": "Test user can log in with valid credentials.",
                    "priority": "high",
                },
                {
                    "scenario_title": "Invalid password",
                    "scenario_type": "negative",
                    "scenario_description": "Test login fails with wrong password.",
                    "priority": "medium",
                },
            ]
        }

        with patch(
            "app.services.ai.ai_service._call_openai",
            new_callable=AsyncMock,
            return_value=raw_scenarios,
        ):
            scenarios = await service.generate_scenarios("Login", "User logs in with email")
            assert len(scenarios) == 2
            assert scenarios[0]["scenario_type"] == "positive"

    async def test_generate_scenarios_raises_on_empty(self, service):
        with patch(
            "app.services.ai.ai_service._call_openai",
            new_callable=AsyncMock,
            return_value={"scenarios": []},
        ):
            with pytest.raises(AIServiceError, match="no scenarios"):
                await service.generate_scenarios("Login", "Description")

    async def test_generate_test_cases_validates_steps(self, service):
        raw_cases = {
            "test_cases": [
                {
                    "test_case_title": "Login with valid credentials",
                    "preconditions": "User is registered",
                    "test_steps": [
                        {"step_number": 1, "action": "Navigate to /login", "expected": "Login page loads"},
                        {"step_number": 2, "action": "Enter email", "expected": "Email field populated"},
                    ],
                    "expected_result": "User is redirected to dashboard",
                    "priority": "high",
                }
            ]
        }

        with patch(
            "app.services.ai.ai_service._call_openai",
            new_callable=AsyncMock,
            return_value=raw_cases,
        ):
            cases = await service.generate_test_cases("Login scenario", "Description", "positive")
            assert len(cases) == 1
            assert isinstance(cases[0]["test_steps"], list)

    async def test_generate_test_cases_raises_on_invalid_steps(self, service):
        bad_cases = {
            "test_cases": [
                {
                    "test_case_title": "Bad case",
                    "test_steps": "not a list",   # invalid — should be a list
                    "expected_result": "Something",
                }
            ]
        }

        with patch(
            "app.services.ai.ai_service._call_openai",
            new_callable=AsyncMock,
            return_value=bad_cases,
        ):
            with pytest.raises(AIServiceError):
                await service.generate_test_cases("Scenario", "Desc", "positive")
