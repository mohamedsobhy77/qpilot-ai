"""
app/schemas/schemas.py

Pydantic v2 request/response schemas for all API endpoints.
Separating schemas from models keeps the API contract decoupled from DB structure.
"""

import uuid
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ─────────────────────────────────────────────────────────────
# Shared / Base
# ─────────────────────────────────────────────────────────────
class APIResponse(BaseModel):
    """Standard envelope for every API response."""
    success: bool
    message: str
    data: Optional[Any] = None


# ─────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = "qa_engineer"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed = {"qa_engineer", "admin"}
        if v not in allowed:
            raise ValueError(f"Role must be one of: {allowed}")
        return v


class UserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Requirements
# ─────────────────────────────────────────────────────────────
class RequirementCreate(BaseModel):
    title: str = Field(min_length=5, max_length=500)
    description: str = Field(min_length=20)


class RequirementResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    status: str
    submitted_by: Optional[uuid.UUID]
    ai_analysis: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RequirementListResponse(BaseModel):
    requirements: List[RequirementResponse]
    total: int


# ─────────────────────────────────────────────────────────────
# Scenarios
# ─────────────────────────────────────────────────────────────
class ScenarioGenerateRequest(BaseModel):
    requirement_id: uuid.UUID


class ScenarioItem(BaseModel):
    scenario_title: str
    scenario_type: str   # positive | negative | edge
    scenario_description: str
    priority: str = "medium"


class ScenarioResponse(BaseModel):
    id: uuid.UUID
    requirement_id: uuid.UUID
    scenario_title: str
    scenario_type: str
    scenario_description: str
    priority: str
    generated_by_ai: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ScenarioListResponse(BaseModel):
    scenarios: List[ScenarioResponse]
    total: int


# ─────────────────────────────────────────────────────────────
# Test Cases
# ─────────────────────────────────────────────────────────────
class TestCaseGenerateRequest(BaseModel):
    scenario_id: uuid.UUID


class TestStep(BaseModel):
    step_number: int
    action: str
    expected: str


class TestCaseResponse(BaseModel):
    id: uuid.UUID
    scenario_id: uuid.UUID
    test_case_title: str
    preconditions: Optional[str]
    test_steps: str   # JSON string
    expected_result: str
    test_data: Optional[str]
    priority: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TestCaseListResponse(BaseModel):
    test_cases: List[TestCaseResponse]
    total: int


# ─────────────────────────────────────────────────────────────
# Approvals
# ─────────────────────────────────────────────────────────────
class ApprovalRequest(BaseModel):
    requirement_id: uuid.UUID
    approval_status: str
    comments: Optional[str] = None

    @field_validator("approval_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"approved", "rejected", "regenerate"}
        if v not in allowed:
            raise ValueError(f"approval_status must be one of: {allowed}")
        return v


class ApprovalResponse(BaseModel):
    id: uuid.UUID
    requirement_id: uuid.UUID
    approved_by: uuid.UUID
    approval_status: str
    comments: Optional[str]
    reviewed_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Automation Scripts
# ─────────────────────────────────────────────────────────────
class AutomationGenerateRequest(BaseModel):
    test_case_id: uuid.UUID
    framework: str = "playwright"


class AutomationScriptResponse(BaseModel):
    id: uuid.UUID
    test_case_id: uuid.UUID
    framework: str
    script_content: str
    script_filename: str
    github_commit_url: Optional[str]
    github_branch: Optional[str]
    generation_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Workflow
# ─────────────────────────────────────────────────────────────
class WorkflowTriggerRequest(BaseModel):
    requirement_id: uuid.UUID


class WorkflowStatusResponse(BaseModel):
    id: uuid.UUID
    workflow_name: str
    requirement_id: Optional[uuid.UUID]
    execution_status: str
    n8n_execution_id: Optional[str]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# Jira Integration
# ─────────────────────────────────────────────────────────────
class JiraCreateRequest(BaseModel):
    related_entity_id: uuid.UUID
    issue_type: str = "Task"
    summary: str = Field(min_length=5, max_length=500)
    description: str


class JiraTicketResponse(BaseModel):
    id: uuid.UUID
    jira_ticket_key: str
    jira_ticket_url: str
    issue_type: str
    summary: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────
# GitHub Integration
# ─────────────────────────────────────────────────────────────
class GitHubPushRequest(BaseModel):
    script_id: uuid.UUID


class GitHubPushResponse(BaseModel):
    script_id: uuid.UUID
    commit_url: str
    branch: str
    message: str


# ─────────────────────────────────────────────────────────────
# Notifications
# ─────────────────────────────────────────────────────────────
class SlackNotifyRequest(BaseModel):
    workflow_execution_id: Optional[uuid.UUID] = None
    message: str


class NotificationResponse(BaseModel):
    id: uuid.UUID
    notification_type: str
    recipient: str
    message: str
    sent_status: bool
    created_at: datetime

    model_config = {"from_attributes": True}
