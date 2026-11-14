"""
Search Result Cache ORM Model
=============================
Purpose:
    Stores and caches web search results retrieved via Tavily to reduce
    redundant external API latency and conserve rate limits.

Milestone Notes:
    - Milestone 1: Data model structure placeholder.
    - Future Milestones: Integrate TTL caching logic and vector embeddings for semantic retrieval.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models import Base


class SearchResultCache(Base):
    """
    Cached search responses and crawled market intelligence snippets.
    """
    __tablename__ = "search_result_caches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idea_id = Column(String(36), ForeignKey("startup_ideas.id"), nullable=True)

    query = Column(String(300), nullable=False, index=True)
    source_url = Column(String(500), nullable=True)
    title = Column(String(300), nullable=True)
    snippet = Column(Text, nullable=False)
    relevance_score = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    idea = relationship("StartupIdea", back_populates="search_caches")
