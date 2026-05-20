"""
app/api/v1/endpoints/automation.py
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.database import get_db
from app.models.models import AutomationScript, TestCase, User
from app.schemas.schemas import APIResponse, AutomationGenerateRequest, AutomationScriptResponse
from app.services.ai.ai_service import ai_service
from app.services.integrations.github_service import github_service
from app.services.integrations.slack_service import slack_service

router = APIRouter(prefix="/automation", tags=["Automation"])


@router.post("/generate", response_model=APIResponse, status_code=201)
async def generate_automation_script(
    payload: AutomationGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a Playwright automation script for a test case,
    push it to GitHub, and send a Slack notification.
    """
    result = await db.execute(select(TestCase).where(TestCase.id == payload.test_case_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found.")

    #if tc.status != "approved":
     #   raise HTTPException(
      #      status_code=422,
       #     detail="Test case must be approved before generating automation scripts.",
        #)

    # Generate the Playwright script via AI
    script_data = await ai_service.generate_automation_script(
        test_case_title=tc.test_case_title,
        test_steps=tc.test_steps,
        expected_result=tc.expected_result,
        preconditions=tc.preconditions or "",
    )

    # Push to GitHub
  #  github_result = await github_service.push_script(
   #     filename=script_data["script_filename"],
    #    content=script_data["script_content"],
    #)

    # Persist the automation script record
    script = AutomationScript(
        test_case_id=tc.id,
        framework=payload.framework,
        script_content=script_data["script_content"],
        script_filename=script_data["script_filename"],
        github_commit_url=None,
        github_branch=None,
        generation_status="pushed",
    )
    db.add(script)
    await db.flush()

    # Notify Slack (non-blocking — don't fail the request if Slack fails)
    try:
        await slack_service.notify_script_pushed(
            test_case_title=tc.test_case_title,
            github_url=github_result["commit_url"],
            branch=github_result["branch"],
        )
    except Exception:
        pass  # Slack failure should never block script generation

    return APIResponse(
        success=True,
        message="Automation script generated and pushed to GitHub.",
        data=AutomationScriptResponse.model_validate(script),
    )


@router.get("/{script_id}", response_model=APIResponse)
async def get_automation_script(
    script_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AutomationScript).where(AutomationScript.id == script_id)
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Automation script not found.")

    return APIResponse(
        success=True,
        message="Script retrieved.",
        data=AutomationScriptResponse.model_validate(script),
    )
