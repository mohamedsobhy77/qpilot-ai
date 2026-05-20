"""
app/api/v1/endpoints/approvals.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.database import get_db
from app.models.models import ApprovalLog, Requirement, User
from app.schemas.schemas import APIResponse, ApprovalRequest, ApprovalResponse

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.post("", response_model=APIResponse, status_code=201)
async def submit_approval(
    payload: ApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """QA engineer approves or rejects generated outputs."""
    result = await db.execute(
        select(Requirement).where(Requirement.id == payload.requirement_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found.")

    log = ApprovalLog(
        requirement_id=req.id,
        approved_by=current_user.id,
        approval_status=payload.approval_status,
        comments=payload.comments,
    )
    db.add(log)

    # Update requirement status based on approval decision
    if payload.approval_status == "approved":
        req.status = "approved"
    elif payload.approval_status == "rejected":
        req.status = "rejected"
    elif payload.approval_status == "regenerate":
        req.status = "analyzed"  # Back to analyzed for re-generation

    await db.flush()

    return APIResponse(
        success=True,
        message=f"Approval recorded: {payload.approval_status}.",
        data=ApprovalResponse.model_validate(log),
    )
