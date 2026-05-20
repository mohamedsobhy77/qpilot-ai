"""
app/api/v1/endpoints/requirements.py

Requirement management endpoints:
  POST /api/v1/requirements         — Submit a new requirement
  GET  /api/v1/requirements         — List all requirements
  GET  /api/v1/requirements/{id}    — Get a single requirement
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.database import get_db
from app.models.models import Requirement, User
from app.schemas.schemas import (
    APIResponse,
    RequirementCreate,
    RequirementListResponse,
    RequirementResponse,
)
from app.services.ai.ai_service import ai_service

import json

router = APIRouter(prefix="/requirements", tags=["Requirements"])


@router.post("", response_model=APIResponse, status_code=201)
async def create_requirement(
    payload: RequirementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a new software requirement.
    Immediately triggers AI analysis and stores the analysis result.
    Status starts as 'analyzing', then moves to 'scenarios_ready' after AI call.
    """
    # Persist the requirement immediately
    req = Requirement(
        title=payload.title,
        description=payload.description,
        submitted_by=current_user.id,
        status="analyzing",
    )
    db.add(req)
    await db.flush()

    # Run AI analysis
    try:
        analysis = await ai_service.analyze_requirement(payload.description)
        req.ai_analysis = json.dumps(analysis)
        req.status = "analyzed"
    except Exception:
        req.status = "failed"

    return APIResponse(
        success=True,
        message="Requirement submitted and analyzed.",
        data=RequirementResponse.model_validate(req),
    )


@router.get("", response_model=APIResponse)
async def list_requirements(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return paginated list of all requirements."""
    count_result = await db.execute(select(func.count(Requirement.id)))
    total = count_result.scalar_one()

    result = await db.execute(
        select(Requirement)
        .order_by(Requirement.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    requirements = result.scalars().all()

    return APIResponse(
        success=True,
        message=f"Found {total} requirements.",
        data=RequirementListResponse(
            requirements=[RequirementResponse.model_validate(r) for r in requirements],
            total=total,
        ),
    )


@router.get("/{requirement_id}", response_model=APIResponse)
async def get_requirement(
    requirement_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single requirement by ID."""
    result = await db.execute(
        select(Requirement).where(Requirement.id == requirement_id)
    )
    req = result.scalar_one_or_none()

    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement '{requirement_id}' not found.",
        )

    return APIResponse(
        success=True,
        message="Requirement retrieved.",
        data=RequirementResponse.model_validate(req),
    )
