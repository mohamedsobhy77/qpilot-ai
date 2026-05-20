"""
app/core/exceptions.py

Domain-specific exception hierarchy.
FastAPI exception handlers in main.py convert these to proper HTTP responses.
"""


class QPilotError(Exception):
    """Base exception for all QPilot application errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(QPilotError):
    """Resource not found (404)."""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} with id '{resource_id}' not found.",
            status_code=404,
        )


class UnauthorizedError(QPilotError):
    """Invalid or missing authentication (401)."""
    def __init__(self, message: str = "Authentication required."):
        super().__init__(message=message, status_code=401)


class ForbiddenError(QPilotError):
    """Authenticated but not authorized (403)."""
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(message=message, status_code=403)


class ValidationError(QPilotError):
    """Input validation failure (422)."""
    def __init__(self, message: str):
        super().__init__(message=message, status_code=422)


class AIServiceError(QPilotError):
    """OpenAI API call failed or returned unusable output (502)."""
    def __init__(self, message: str = "AI service returned an invalid response."):
        super().__init__(message=message, status_code=502)


class IntegrationError(QPilotError):
    """External integration failure: Jira, GitHub, Slack (502)."""
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"{service} integration error: {message}",
            status_code=502,
        )


class ConflictError(QPilotError):
    """Resource already exists (409)."""
    def __init__(self, message: str):
        super().__init__(message=message, status_code=409)
