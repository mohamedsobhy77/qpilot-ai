"""
app/api/v1/endpoints/scenarios.py
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.database import get_db
from app.models.models import Requirement, TestScenario, User
from app.schemas.schemas import APIResponse, ScenarioGenerateRequest, ScenarioListResponse, ScenarioResponse
from app.services.ai.ai_service import ai_service

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.post("/generate", response_model=APIResponse, status_code=201)
async def generate_scenarios(
    payload: ScenarioGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AI test scenarios for a requirement."""
    result = await db.execute(select(Requirement).where(Requirement.id == payload.requirement_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found.")

    scenarios_data = await ai_service.generate_scenarios(req.title, req.description)

    created = []
    for s in scenarios_data:
        scenario = TestScenario(
            requirement_id=req.id,
            scenario_title=s["scenario_title"],
            scenario_type=s["scenario_type"],
            scenario_description=s["scenario_description"],
            priority=s.get("priority", "medium"),
        )
        db.add(scenario)
        created.append(scenario)

    await db.flush()

    req.status = "scenarios_ready"

    return APIResponse(
        success=True,
        message=f"Generated {len(created)} scenarios.",
        data=ScenarioListResponse(
            scenarios=[ScenarioResponse.model_validate(s) for s in created],
            total=len(created),
        ),
    )


@router.get("/{requirement_id}", response_model=APIResponse)
async def get_scenarios(
    requirement_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(TestScenario).where(TestScenario.requirement_id == requirement_id)
    )
    scenarios = result.scalars().all()
    return APIResponse(
        success=True,
        message=f"Found {len(scenarios)} scenarios.",
        data=ScenarioListResponse(
            scenarios=[ScenarioResponse.model_validate(s) for s in scenarios],
            total=len(scenarios),
        ),
    )
