"""
app/api/v1/router.py

Registers all v1 endpoint routers onto a single APIRouter.
This is included in main.py with prefix="/api/v1".
"""

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.requirements import router as requirements_router
from app.api.v1.endpoints.scenarios import router as scenarios_router
from app.api.v1.endpoints.test_cases import router as test_cases_router
from app.api.v1.endpoints.test_cases_bulk import router as test_cases_bulk_router
from app.api.v1.endpoints.approvals import router as approvals_router
from app.api.v1.endpoints.automation import router as automation_router
from app.api.v1.endpoints.integrations import (
    jira_router,
    slack_router,
    workflow_router,
)

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(requirements_router)
api_router.include_router(scenarios_router)
api_router.include_router(test_cases_router)
api_router.include_router(test_cases_bulk_router)
api_router.include_router(approvals_router)
api_router.include_router(automation_router)
api_router.include_router(jira_router)
api_router.include_router(slack_router)
api_router.include_router(workflow_router)
