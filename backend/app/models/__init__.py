"""
Database Models Module
======================
SQLAlchemy 2.0 ORM Declarative Models for PostgreSQL persistence.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.idea import StartupIdea, ValidationReport
from app.models.search_result import SearchResultCache

__all__ = ["Base", "StartupIdea", "ValidationReport", "SearchResultCache"]
