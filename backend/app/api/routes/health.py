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

from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, status
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    response_description="Returns runtime status and server environment",
)
async def check_health() -> Dict[str, Any]:
    """
    Performs basic liveness probe verifying that the FastAPI ASGI application
    is running and responsive.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
