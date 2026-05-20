"""
app/core/logging.py

Structured logging configuration using structlog.
In development: pretty colored console output.
In production: JSON output suitable for log aggregators (Datadog, CloudWatch).
"""

import logging
import sys

import structlog

from app.core.config import settings


def configure_logging() -> None:
    """Call once at application startup in main.py."""

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_production:
        # JSON lines — parseable by any log aggregator
        renderer = structlog.processors.JSONRenderer()
    else:
        # Colorful dev output
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)


def get_logger(name: str):
    """Return a bound structlog logger for the given module name."""
    return structlog.get_logger(name)
