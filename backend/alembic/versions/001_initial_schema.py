"""initial_schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users ─────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="qa_engineer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ── requirements ──────────────────────────────────────────────
    op.create_table(
        "requirements",
        sa.Column("id", UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("submitted_by", UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="submitted"),
        sa.Column("ai_analysis", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["submitted_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_requirements_status", "requirements", ["status"])
    op.create_index("ix_requirements_submitted_by", "requirements", ["submitted_by"])

    # ── test_scenarios ────────────────────────────────────────────
    op.create_table(
        "test_scenarios",
        sa.Column("id", UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("requirement_id", UUID(as_uuid=True), nullable=False),
        sa.Column("scenario_title", sa.String(500), nullable=False),
        sa.Column("scenario_type", sa.String(50), nullable=False),
        sa.Column("scenario_description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("generated_by_ai", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_test_scenarios_requirement_id", "test_scenarios", ["requirement_id"])

    # ── test_cases ────────────────────────────────────────────────
    op.create_table(
        "test_cases",
        sa.Column("id", UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("scenario_id", UUID(as_uuid=True), nullable=False),
        sa.Column("test_case_title", sa.String(500), nullable=False),
        sa.Column("preconditions", sa.Text(), nullable=True),
        sa.Column("test_steps", sa.Text(), nullable=False),   # JSON array
        sa.Column("expected_result", sa.Text(), nullable=False),
        sa.Column("test_data", sa.Text(), nullable=True),      # JSON blob
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["scenario_id"], ["test_scenarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_test_cases_scenario_id", "test_cases", ["scenario_id"])
    op.create_index("ix_test_cases_status", "test_cases", ["status"])

    # ── automation_scripts ────────────────────────────────────────
    op.create_table(
        "automation_scripts",
        sa.Column("id", UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("test_case_id", UUID(as_uuid=True), nullable=False),
        sa.Column("framework", sa.String(50), nullable=False, server_default="playwright"),
        sa.Column("script_content", sa.Text(), nullable=False),
        sa.Column("script_filename", sa.String(255), nullable=False),
        sa.Column("github_commit_url", sa.Text(), nullable=True),
        sa.Column("github_branch", sa.String(255), nullable=True),
        sa.Column("generation_status", sa.String(50), nullable=False, server_default="generated"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["test_case_id"], ["test_cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("test_case_id"),
    )

    # ── jira_tickets ──────────────────────────────────────────────
    op.create_table(
        "jira_tickets",
        sa.Column("id", UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("related_entity_id", UUID(as_uuid=True), nullable=False),
        sa.Column("jira_ticket_key", sa.String(100), nullable=False),
        sa.Column("jira_ticket_url", sa.Text(), nullable=False),
        sa.Column("issue_type", sa.String(50), nullable=False, server_default="Task"),
        sa.Column("summary", sa.String(500), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("jira_ticket_key"),
    )

    # ── workflow_executions ───────────────────────────────────────
    op.create_table(
        "workflow_executions",
        sa.Column("id", UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workflow_name", sa.String(255), nullable=False),
        sa.Column("requirement_id", UUID(as_uuid=True), nullable=True),
        sa.Column("triggered_by", UUID(as_uuid=True), nullable=True),
        sa.Column("execution_status", sa.String(50), nullable=False, server_default="running"),
        sa.Column("n8n_execution_id", sa.String(255), nullable=True),
        sa.Column("logs", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"]),
        sa.ForeignKeyConstraint(["triggered_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workflow_executions_status", "workflow_executions", ["execution_status"])

    # ── notifications ─────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workflow_execution_id", UUID(as_uuid=True), nullable=True),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column("recipient", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("sent_status", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workflow_execution_id"], ["workflow_executions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── approval_logs ─────────────────────────────────────────────
    op.create_table(
        "approval_logs",
        sa.Column("id", UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("requirement_id", UUID(as_uuid=True), nullable=False),
        sa.Column("approved_by", UUID(as_uuid=True), nullable=False),
        sa.Column("approval_status", sa.String(50), nullable=False),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("approval_logs")
    op.drop_table("notifications")
    op.drop_table("workflow_executions")
    op.drop_table("jira_tickets")
    op.drop_table("automation_scripts")
    op.drop_table("test_cases")
    op.drop_table("test_scenarios")
    op.drop_table("requirements")
    op.drop_table("users")
