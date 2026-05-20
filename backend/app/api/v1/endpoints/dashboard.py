"""
app/api/v1/endpoints/dashboard.py

Dashboard statistics endpoint:
  GET /api/v1/dashboard/stats  — Returns aggregate counts + recent requirements
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.database import get_db
from app.models.models import (
    AutomationScript, Requirement, TestCase, TestScenario, User
)
from app.schemas.schemas import APIResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=APIResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return aggregate platform statistics for the dashboard overview.
    Runs 5 lightweight COUNT queries in sequence.
    """

    # Total requirements
    total_requirements = (
        await db.execute(select(func.count(Requirement.id)))
    ).scalar_one()

    # Total scenarios
    total_scenarios = (
        await db.execute(select(func.count(TestScenario.id)))
    ).scalar_one()

    # Total test cases
    total_test_cases = (
        await db.execute(select(func.count(TestCase.id)))
    ).scalar_one()

    # Total automation scripts generated
    total_scripts_generated = (
        await db.execute(select(func.count(AutomationScript.id)))
    ).scalar_one()

    # Pending approvals (requirements with test cases ready but not yet approved)
    pending_approvals = (
        await db.execute(
            select(func.count(Requirement.id)).where(
                Requirement.status == "test_cases_ready"
            )
        )
    ).scalar_one()

    # Recent requirements (last 5)
    recent_result = await db.execute(
        select(Requirement)
        .order_by(Requirement.created_at.desc())
        .limit(5)
    )
    recent_requirements = recent_result.scalars().all()

    from app.schemas.schemas import RequirementResponse

    return APIResponse(
        success=True,
        message="Dashboard stats retrieved.",
        data={
            "total_requirements": total_requirements,
            "total_scenarios": total_scenarios,
            "total_test_cases": total_test_cases,
            "total_scripts_generated": total_scripts_generated,
            "pending_approvals": pending_approvals,
            "recent_requirements": [
                RequirementResponse.model_validate(r) for r in recent_requirements
            ],
        },
    )
