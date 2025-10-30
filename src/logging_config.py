#!/usr/bin/env python3
"""
Structured logging configuration using structlog with JSON output by default.
Supports LOG_LEVEL and LOG_FORMAT env vars. Correlation IDs are injected via
structlog contextvars.
"""

import logging
import os
from typing import Optional

import structlog


def configure_logging(log_level: Optional[str] = None, log_format: Optional[str] = None) -> None:
    """
    Configure global logging. Idempotent.

    Env overrides:
    - LOG_LEVEL: DEBUG|INFO|WARNING|ERROR (default INFO)
    - LOG_FORMAT: json|console (default json)
    """
    level_name = (log_level or os.getenv("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)
    fmt = (log_format or os.getenv("LOG_FORMAT", "json")).lower()

    # Base stdlib logging
    logging.basicConfig(level=level, format="%(message)s")

    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if fmt == "console":
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            renderer,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """Return a bound structured logger."""
    return structlog.get_logger(name)


