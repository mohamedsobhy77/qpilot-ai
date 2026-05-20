"""
app/api/v1/endpoints/integrations.py

External integration endpoints:
  POST /api/v1/integrations/jira/create  — Create Jira ticket
  POST /api/v1/integrations/slack/notify — Send Slack notification
  POST /api/v1/workflows/trigger         — Trigger n8n workflow
  GET  /api/v1/workflows/{id}            — Get workflow status
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.database import get_db
from app.models.models import JiraTicket, Notification, Requirement, WorkflowExecution, User
from app.schemas.schemas import (
    APIResponse,
    JiraCreateRequest,
    JiraTicketResponse,
    SlackNotifyRequest,
    NotificationResponse,
    WorkflowTriggerRequest,
    WorkflowStatusResponse,
)
from app.services.integrations.jira_service import jira_service
from app.services.integrations.slack_service import slack_service

jira_router = APIRouter(prefix="/integrations/jira", tags=["Jira"])
slack_router = APIRouter(prefix="/integrations/slack", tags=["Slack"])
workflow_router = APIRouter(prefix="/workflows", tags=["Workflows"])


# ─────────────────────────────────────────────────────────────
# Jira
# ─────────────────────────────────────────────────────────────
@jira_router.post("/create", response_model=APIResponse, status_code=201)
async def create_jira_ticket(
    payload: JiraCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a Jira issue and store the ticket reference."""
    result = await jira_service.create_issue(
        summary=payload.summary,
        description=payload.description,
        issue_type=payload.issue_type,
    )

    ticket = JiraTicket(
        related_entity_id=payload.related_entity_id,
        jira_ticket_key=result["jira_ticket_key"],
        jira_ticket_url=result["jira_ticket_url"],
        issue_type=payload.issue_type,
        summary=payload.summary,
    )
    db.add(ticket)
    await db.flush()

    return APIResponse(
        success=True,
        message=f"Jira ticket {result['jira_ticket_key']} created.",
        data=JiraTicketResponse.model_validate(ticket),
    )


# ─────────────────────────────────────────────────────────────
# Slack
# ─────────────────────────────────────────────────────────────
@slack_router.post("/notify", response_model=APIResponse)
async def send_slack_notification(
    payload: SlackNotifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a Slack notification and record it."""
    await slack_service.send_message(text=payload.message)

    notification = Notification(
        workflow_execution_id=payload.workflow_execution_id,
        notification_type="slack",
        recipient="slack-channel",
        message=payload.message,
        sent_status=True,
    )
    db.add(notification)
    await db.flush()

    return APIResponse(
        success=True,
        message="Slack notification sent.",
        data=NotificationResponse.model_validate(notification),
    )


# ─────────────────────────────────────────────────────────────
# Workflows
# ─────────────────────────────────────────────────────────────
@workflow_router.post("/trigger", response_model=APIResponse, status_code=201)
async def trigger_workflow(
    payload: WorkflowTriggerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Record a new workflow execution.
    In production, n8n calls this API (or this API calls n8n webhook).
    """
    result = await db.execute(
        select(Requirement).where(Requirement.id == payload.requirement_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found.")

    execution = WorkflowExecution(
        workflow_name="qpilot-main-workflow",
        requirement_id=req.id,
        triggered_by=current_user.id,
        execution_status="running",
    )
    db.add(execution)
    await db.flush()

    return APIResponse(
        success=True,
        message="Workflow triggered.",
        data=WorkflowStatusResponse.model_validate(execution),
    )


@workflow_router.get("/{workflow_id}", response_model=APIResponse)
async def get_workflow_status(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current status of a workflow execution."""
    result = await db.execute(
        select(WorkflowExecution).where(WorkflowExecution.id == workflow_id)
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Workflow execution not found.")

    return APIResponse(
        success=True,
        message="Workflow status retrieved.",
        data=WorkflowStatusResponse.model_validate(execution),
    )
