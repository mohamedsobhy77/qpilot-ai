"""
app/api/v1/endpoints/test_cases.py
"""

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.database import get_db
from app.models.models import TestCase, TestScenario, User
from app.schemas.schemas import APIResponse, TestCaseGenerateRequest, TestCaseListResponse, TestCaseResponse
from app.services.ai.ai_service import ai_service

router = APIRouter(prefix="/test-cases", tags=["Test Cases"])


@router.post("/generate", response_model=APIResponse, status_code=201)
async def generate_test_cases(
    payload: TestCaseGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AI test cases for a scenario."""
    result = await db.execute(select(TestScenario).where(TestScenario.id == payload.scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found.")

    test_cases_data = await ai_service.generate_test_cases(
        scenario.scenario_title,
        scenario.scenario_description,
        scenario.scenario_type,
    )

    created = []
    for tc in test_cases_data:
        test_case = TestCase(
            scenario_id=scenario.id,
            test_case_title=tc["test_case_title"],
            preconditions=tc.get("preconditions", ""),
            test_steps=json.dumps(tc["test_steps"]),
            expected_result=tc["expected_result"],
            test_data=json.dumps(tc.get("test_data", {})),
            priority=tc.get("priority", "medium"),
            status="draft",
        )
        db.add(test_case)
        created.append(test_case)

    await db.flush()

    return APIResponse(
        success=True,
        message=f"Generated {len(created)} test cases.",
        data=TestCaseListResponse(
            test_cases=[TestCaseResponse.model_validate(tc) for tc in created],
            total=len(created),
        ),
    )


@router.get("/{scenario_id}", response_model=APIResponse)
async def get_test_cases(
    scenario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(TestCase).where(TestCase.scenario_id == scenario_id)
    )
    test_cases = result.scalars().all()
    return APIResponse(
        success=True,
        message=f"Found {len(test_cases)} test cases.",
        data=TestCaseListResponse(
            test_cases=[TestCaseResponse.model_validate(tc) for tc in test_cases],
            total=len(test_cases),
        ),
    )
