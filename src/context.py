#!/usr/bin/env python3
"""
Request/run context utilities. Provides a correlation_id using contextvars
that is automatically merged into structlog logs via logging_config.
"""

import uuid
from contextvars import ContextVar

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


def new_correlation_id() -> str:
    cid = uuid.uuid4().hex[:12]
    correlation_id_var.set(cid)
    return cid


def set_correlation_id(value: str) -> None:
    correlation_id_var.set(value)


def get_correlation_id() -> str:
    return correlation_id_var.get() or ""


