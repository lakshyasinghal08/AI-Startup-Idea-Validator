"""
FastAPI Application Entry Point
===============================
Purpose:
    Initializes the FastAPI ASGI web application, configures CORS policies,
    registers domain routes, and establishes lifespan lifecycle hooks.

Milestone Notes:
    - Milestone 1: Production-ready application factory with health, idea, and search routers.
    - Future Milestones: Attach database lifespan managers and background task brokers.
"""

import os
import sys
from contextlib import asynccontextmanager

# Ensure backend root directory is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, ".."))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.api.routes import health_router, idea_router, search_router
from app.core.config import settings
from app.core.logging import logger
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager for startup and shutdown events.
    """
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Port: {settings.PORT}")
    logger.info(f"API Docs available at: http://localhost:{settings.PORT}/docs")
    logger.info("=" * 60)

    yield  # Application processes requests during this block

    logger.info("Shutting down application gracefully...")


def create_application() -> FastAPI:
    """
    Application factory configuring middleware and routing endpoints.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Enterprise Multi-Agent AI system for validating startup ideas, "
            "sizing target markets, discovering competitors, and synthesizing SWOT dossiers. "
            "Infosys Springboard Virtual Internship 7.0 - Milestone 1."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Cross-Origin Resource Sharing (CORS) Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Domain API Routers with Versioned Prefix (/api/v1)
    app.include_router(health_router, prefix=settings.API_PREFIX)
    app.include_router(idea_router, prefix=settings.API_PREFIX)
    app.include_router(search_router, prefix=settings.API_PREFIX)

    # Standardized Exception Handling for Clean JSON Error Envelopes
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
            headers=exc.headers,
        )

    # Root Endpoint
    @app.get(
        "/",
        status_code=status.HTTP_200_OK,
        tags=["Root"],
        summary="Service Root Status",
    )
    async def root():
        return JSONResponse(
            content={
                "project": settings.APP_NAME,
                "version": "1.0.0",
                "status": "online",
                "docs": "/docs",
                "health": f"{settings.API_PREFIX}/health/",
            }
        )

    return app


# Application singleton instance for ASGI servers (Uvicorn / Gunicorn)
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
