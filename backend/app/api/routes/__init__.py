"""
API Route Handlers
==================
Exports router instances for health, idea validation, and market search.
"""

from app.api.routes.health import router as health_router
from app.api.routes.idea import router as idea_router
from app.api.routes.search import router as search_router

__all__ = ["health_router", "idea_router", "search_router"]
