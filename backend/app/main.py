"""
app/main.py

QPilot AI — FastAPI Application Entry Point.

Responsibilities:
  - Create the FastAPI app instance
  - Register middleware (CORS, logging, rate limiting)
  - Register exception handlers
  - Include all API routers
  - Handle startup/shutdown lifecycle events
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import QPilotError
from app.core.logging import configure_logging, get_logger
from app.db.database import engine
from app.models.models import Base

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Startup: create DB tables (dev only — use Alembic in production).
    Shutdown: dispose DB engine.
    """
    logger.info("qpilot_startup", env=settings.app_env)

    # Auto-create tables in development (Alembic handles production)
    if not settings.is_production:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("db_tables_created")

    yield

    await engine.dispose()
    logger.info("qpilot_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="AI-Powered QA Automation & Workflow Orchestration Platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handlers ──────────────────────────────────
    @app.exception_handler(QPilotError)
    async def qpilot_error_handler(request: Request, exc: QPilotError):
        """Convert domain exceptions to structured JSON error responses."""
        logger.warning(
            "domain_error",
            status_code=exc.status_code,
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.message, "data": None},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        """Catch-all for unexpected errors — never expose raw tracebacks."""
        logger.error(
            "unhandled_error",
            path=request.url.path,
            error=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "An internal server error occurred. Please try again.",
                "data": None,
            },
        )

    # ── Routes ──────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Simple liveness probe for load balancers and Docker healthchecks."""
        return {"status": "healthy", "app": settings.app_name, "env": settings.app_env}

    return app


app = create_app()
