"""
Health Check API Route
======================
Purpose:
    Provides service liveness, readiness, and runtime metadata probes.
    Crucial for automated health checks on Render, Docker containers, and CI pipelines.

Milestone Notes:
    - Milestone 1: Server and environment liveness status.
    - Future Milestones: Add database connectivity and LLM service reachability probes.
"""

import os
import sys
from datetime import UTC, datetime
from typing import Any

# Ensure backend root directory is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../../.."))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.config import settings
from fastapi import APIRouter, status

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    response_description="Returns runtime status and server environment",
)
@router.get(
    "",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def check_health() -> dict[str, Any]:
    """
    Performs basic liveness probe verifying that the FastAPI ASGI application
    is running and responsive.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
    }


if __name__ == "__main__":
    print("Health Check Route Module Loaded Successfully!")
    print("Health Status:", check_health())
