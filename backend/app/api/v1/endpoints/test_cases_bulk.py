"""
app/api/v1/endpoints/test_cases_bulk.py

Adds a bulk generation endpoint used by n8n:
  POST /api/v1/test-cases/generate-all

Given a requirement_id, it iterates every scenario for that requirement
and generates test cases for each one in sequence.
"""

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.database import get_db
from app.models.models import Requirement, TestCase, TestScenario, User
from app.schemas.schemas import APIResponse
from app.services.ai.ai_service import ai_service

router = APIRouter(prefix="/test-cases", tags=["Test Cases"])


class BulkGenerateRequest(BaseModel):
    requirement_id: str


@router.post("/generate-all", response_model=APIResponse, status_code=201)
async def generate_all_test_cases(
    payload: BulkGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk-generate test cases for every scenario attached to a requirement.
    Called by n8n after scenario generation completes.
    """
    # Validate requirement exists
    req_result = await db.execute(
        select(Requirement).where(Requirement.id == payload.requirement_id)
    )
    req = req_result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found.")

    # Fetch all scenarios
    scenarios_result = await db.execute(
        select(TestScenario).where(TestScenario.requirement_id == req.id)
    )
    scenarios = scenarios_result.scalars().all()

    if not scenarios:
        raise HTTPException(
            status_code=422,
            detail="No scenarios found for this requirement. Generate scenarios first.",
        )

    total_created = 0
    errors = []

    for scenario in scenarios:
        try:
            test_cases_data = await ai_service.generate_test_cases(
                scenario.scenario_title,
                scenario.scenario_description,
                scenario.scenario_type,
            )
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
                total_created += 1
        except Exception as exc:
            errors.append(f"Scenario '{scenario.scenario_title}': {str(exc)}")

    await db.flush()

    # Advance requirement status
    req.status = "test_cases_ready"

    return APIResponse(
        success=True,
        message=f"Generated {total_created} test cases across {len(scenarios)} scenarios."
        + (f" Errors: {len(errors)}" if errors else ""),
        data={
            "total_created": total_created,
            "scenarios_processed": len(scenarios),
            "errors": errors,
        },
    )
