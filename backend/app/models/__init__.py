"""
Domain Models Package
=====================
Defines application domain entities for Startup Ideas, Validation Reports,
and Search Result Caches.

Milestone Notes:
    - Milestone 1: Pure in-memory domain models. No PostgreSQL or database drivers required.
    - Milestone 5: Integration with PostgreSQL using SQLAlchemy 2.0 and Alembic.
"""

from app.models.idea import StartupIdea, ValidationReport
from app.models.search_result import SearchResultCache

__all__ = ["SearchResultCache", "StartupIdea", "ValidationReport"]
