"""
app/models/models.py

SQLAlchemy ORM models for all 9 QPilot database tables.
All primary keys are UUIDs. All timestamps are UTC.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, String, Text, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


# ─────────────────────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="qa_engineer")  # qa_engineer | admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    requirements: Mapped[list["Requirement"]] = relationship(back_populates="submitter")
    approval_logs: Mapped[list["ApprovalLog"]] = relationship(back_populates="approver")
    workflow_executions: Mapped[list["WorkflowExecution"]] = relationship(back_populates="triggered_by_user")


# ─────────────────────────────────────────────────────────────
# Requirements
# ─────────────────────────────────────────────────────────────
class Requirement(Base):
    __tablename__ = "requirements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="submitted"
        # submitted | analyzing | scenarios_ready | test_cases_ready
        # approved | automation_generated | completed | failed
    )
    ai_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON blob
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )

    # Relationships
    submitter: Mapped["User"] = relationship(back_populates="requirements")
    test_scenarios: Mapped[list["TestScenario"]] = relationship(back_populates="requirement")
    approval_logs: Mapped[list["ApprovalLog"]] = relationship(back_populates="requirement")

    __table_args__ = (
        Index("ix_requirements_status", "status"),
        Index("ix_requirements_submitted_by", "submitted_by"),
    )


# ─────────────────────────────────────────────────────────────
# Test Scenarios
# ─────────────────────────────────────────────────────────────
class TestScenario(Base):
    __tablename__ = "test_scenarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False
    )
    scenario_title: Mapped[str] = mapped_column(String(500), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(50), nullable=False)  # positive | negative | edge
    scenario_description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium")   # high | medium | low
    generated_by_ai: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    requirement: Mapped["Requirement"] = relationship(back_populates="test_scenarios")
    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="scenario")
    jira_tickets: Mapped[list["JiraTicket"]] = relationship(
        back_populates="scenario",
        primaryjoin="JiraTicket.related_entity_id == TestScenario.id",
        foreign_keys="JiraTicket.related_entity_id",
    )

    __table_args__ = (
        Index("ix_test_scenarios_requirement_id", "requirement_id"),
    )


# ─────────────────────────────────────────────────────────────
# Test Cases
# ─────────────────────────────────────────────────────────────
class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("test_scenarios.id", ondelete="CASCADE"), nullable=False
    )
    test_case_title: Mapped[str] = mapped_column(String(500), nullable=False)
    preconditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    test_steps: Mapped[str] = mapped_column(Text, nullable=False)         # JSON array
    expected_result: Mapped[str] = mapped_column(Text, nullable=False)
    test_data: Mapped[str | None] = mapped_column(Text, nullable=True)    # JSON blob
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(50), default="draft")      # draft | approved | rejected
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    scenario: Mapped["TestScenario"] = relationship(back_populates="test_cases")
    automation_script: Mapped["AutomationScript | None"] = relationship(
        back_populates="test_case", uselist=False
    )

    __table_args__ = (
        Index("ix_test_cases_scenario_id", "scenario_id"),
        Index("ix_test_cases_status", "status"),
    )


# ─────────────────────────────────────────────────────────────
# Automation Scripts
# ─────────────────────────────────────────────────────────────
class AutomationScript(Base):
    __tablename__ = "automation_scripts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    test_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("test_cases.id", ondelete="CASCADE"), unique=True
    )
    framework: Mapped[str] = mapped_column(String(50), default="playwright")
    script_content: Mapped[str] = mapped_column(Text, nullable=False)
    script_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    github_commit_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    github_branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    generation_status: Mapped[str] = mapped_column(
        String(50), default="generated"   # generated | pushed | failed
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    test_case: Mapped["TestCase"] = relationship(back_populates="automation_script")


# ─────────────────────────────────────────────────────────────
# Jira Tickets
# ─────────────────────────────────────────────────────────────
class JiraTicket(Base):
    __tablename__ = "jira_tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    related_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    jira_ticket_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    jira_ticket_url: Mapped[str] = mapped_column(Text, nullable=False)
    issue_type: Mapped[str] = mapped_column(String(50), default="Task")   # Bug | Task | Story
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Polymorphic relationship — can link to scenario or test case
    scenario: Mapped["TestScenario"] = relationship(
        back_populates="jira_tickets",
        primaryjoin="JiraTicket.related_entity_id == TestScenario.id",
        foreign_keys=[related_entity_id],
        viewonly=True,
    )


# ─────────────────────────────────────────────────────────────
# Workflow Executions
# ─────────────────────────────────────────────────────────────
class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    requirement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("requirements.id"), nullable=True
    )
    triggered_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    execution_status: Mapped[str] = mapped_column(
        String(50), default="running"    # running | success | failed
    )
    n8n_execution_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logs: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    triggered_by_user: Mapped["User"] = relationship(back_populates="workflow_executions")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="workflow_execution")

    __table_args__ = (
        Index("ix_workflow_executions_status", "execution_status"),
    )


# ─────────────────────────────────────────────────────────────
# Notifications
# ─────────────────────────────────────────────────────────────
class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workflow_execution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_executions.id"), nullable=True
    )
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)  # slack | email
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sent_status: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    workflow_execution: Mapped["WorkflowExecution"] = relationship(back_populates="notifications")


# ─────────────────────────────────────────────────────────────
# Approval Logs
# ─────────────────────────────────────────────────────────────
class ApprovalLog(Base):
    __tablename__ = "approval_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("requirements.id", ondelete="CASCADE")
    )
    approved_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    approval_status: Mapped[str] = mapped_column(
        String(50), nullable=False    # approved | rejected | regenerate
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    requirement: Mapped["Requirement"] = relationship(back_populates="approval_logs")
    approver: Mapped["User"] = relationship(back_populates="approval_logs")
