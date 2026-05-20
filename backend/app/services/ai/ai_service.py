"""
app/services/ai/ai_service.py

Core AI service layer.
Wraps OpenAI API calls with:
  - Automatic retry with exponential backoff (tenacity)
  - Strict JSON response parsing and validation
  - Structured logging for every AI call
  - Hallucination prevention via response constraints
"""

import json
from typing import Any

from openai import AsyncOpenAI, RateLimitError, APIStatusError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)
import logging

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.core.logging import get_logger
from app.services.ai.prompts import PromptManager

logger = get_logger(__name__)

# OpenAI async client — created once at module level
_client = AsyncOpenAI(
    api_key=settings.openai_api_key,
    base_url="https://openrouter.ai/api/v1"
)


def _retry_decorator():
    """
    Retry up to 3 times on rate limit or server errors.
    Exponential backoff: 2s → 4s → 8s.
    """
    return retry(
        retry=retry_if_exception_type((RateLimitError, APIStatusError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
        reraise=True,
    )


def _parse_json_response(content: str, context: str) -> dict:
    """
    Parse and return the JSON from an AI response string.
    Handles cases where the model wraps JSON in markdown code fences.

    Raises:
        AIServiceError: If the response cannot be parsed as valid JSON.
    """
    # Strip markdown code fences if present
    cleaned = content.strip()

    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]).strip()

    try:
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1

        if start != -1 and end != -1:
            cleaned = cleaned[start:end]

        print("\n\nAI RAW RESPONSE:\n", cleaned)
        return json.loads(cleaned)

    except json.JSONDecodeError as e:
        logger.error(
            "ai_json_parse_failed",
            context=context,
            raw_content=content[:500],
            error=str(e),
        )

        raise AIServiceError(
            f"AI returned invalid JSON for '{context}'. "
            "The response could not be parsed. Please try again."
        )

async def _call_openai(
    system_prompt: str,
    user_prompt: str,
    context: str,
) -> dict:
    """
    Make a single OpenAI chat completion call and return parsed JSON.

    Args:
        system_prompt: Persona and output rules.
        user_prompt: The specific content for this request.
        context: Human-readable label for logging (e.g. "requirement_analysis").
    """
    logger.info("ai_call_start", context=context, model=settings.openai_model)

    @_retry_decorator()
    async def _make_request() -> Any:
        return await _client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=settings.openai_max_tokens,
            temperature=settings.openai_temperature,
          #  response_format={"type": "json_object"},   # Force JSON mode
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

    try:
        response = await _make_request()
    except (RateLimitError, APIStatusError) as e:
        logger.error("ai_call_failed", context=context, error=str(e))
        raise AIServiceError(f"OpenAI API error during '{context}': {str(e)}")

    content = response.choices[0].message.content or ""
    token_usage = response.usage

    logger.info(
        "ai_call_success",
        context=context,
        prompt_tokens=token_usage.prompt_tokens if token_usage else 0,
        completion_tokens=token_usage.completion_tokens if token_usage else 0,
    )

    return _parse_json_response(content, context)


class AIService:
    """
    High-level AI service used by routers/services.
    Each method maps to one prompt template and returns typed Python dicts.
    """

    async def analyze_requirement(self, description: str) -> dict:
        """Analyze a requirement and return testing insights."""
        system, user = PromptManager.requirement_analysis(description)
        return await _call_openai(system, user, "requirement_analysis")

    async def generate_scenarios(
        self,
        requirement_title: str,
        requirement_description: str,
    ) -> list[dict]:
        """Generate test scenarios for a requirement. Returns list of scenario dicts."""
        system, user = PromptManager.scenario_generation(
            requirement_title, requirement_description
        )
        result = await _call_openai(system, user, "scenario_generation")

        scenarios = result.get("scenarios", [])
        if not scenarios:
            raise AIServiceError("AI returned no scenarios. Please try again.")

        # Validate each scenario has required fields
        required_fields = {"scenario_title", "scenario_type", "scenario_description"}
        for i, s in enumerate(scenarios):
            missing = required_fields - s.keys()
            if missing:
                raise AIServiceError(
                    f"Scenario {i+1} is missing required fields: {missing}"
                )
            # Normalize scenario_type
            if s["scenario_type"] not in {"positive", "negative", "edge"}:
                s["scenario_type"] = "positive"
            # Normalize priority
            if s.get("priority") not in {"high", "medium", "low"}:
                s["priority"] = "medium"

        return scenarios

    async def generate_test_cases(
        self,
        scenario_title: str,
        scenario_description: str,
        scenario_type: str,
    ) -> list[dict]:
        """Generate test cases for a scenario. Returns list of test case dicts."""
        system, user = PromptManager.test_case_generation(
            scenario_title, scenario_description, scenario_type
        )
        result = await _call_openai(system, user, "test_case_generation")

        test_cases = result.get("test_cases", [])
        if not test_cases:
            raise AIServiceError("AI returned no test cases. Please try again.")

        required_fields = {"test_case_title", "test_steps", "expected_result"}
        for i, tc in enumerate(test_cases):
            missing = required_fields - tc.keys()
            if missing:
                raise AIServiceError(
                    f"Test case {i+1} is missing required fields: {missing}"
                )
            # Ensure test_steps is a list
            if not isinstance(tc.get("test_steps"), list):
                raise AIServiceError(f"Test case {i+1} has invalid test_steps format.")
            # Normalize priority
            if tc.get("priority") not in {"high", "medium", "low"}:
                tc["priority"] = "medium"

        return test_cases

    async def generate_automation_script(
        self,
        test_case_title: str,
        test_steps: str,
        expected_result: str,
        preconditions: str = "",
    ) -> dict:
        """Generate a Playwright automation script. Returns dict with script_content etc."""
        system, user = PromptManager.automation_script_generation(
            test_case_title, test_steps, expected_result, preconditions
        )
        result = await _call_openai(system, user, "automation_script_generation")

        required = {"script_filename", "script_content"}
        missing = required - result.keys()
        if missing:
            raise AIServiceError(
                f"AI script response is missing required fields: {missing}"
            )

        return result

    async def validate_outputs(self, generated_test_cases: str) -> dict:
        """Run QA validation review on generated test cases."""
        system, user = PromptManager.validation_review(generated_test_cases)
        return await _call_openai(system, user, "validation_review")


# Module-level singleton — import this in services and routers
ai_service = AIService()
