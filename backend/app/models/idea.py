"""
Startup Idea & Validation Report ORM Models
===========================================
Purpose:
    Defines database tables for persisting startup idea submissions,
    agent execution status, scores, SWOT analysis, and generated reports.

Milestone Notes:
    - Milestone 1: Declarative class models defined with SQLAlchemy 2.0.
    - Future Milestones: Connect to Alembic migrations and PostgreSQL instance.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    DateTime,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models import Base


class StartupIdea(Base):
    """
    Represents an entrepreneur's submitted startup idea and its lifecycle status.
    """
    __tablename__ = "startup_ideas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    target_market = Column(String(150), nullable=False)
    target_audience = Column(String(255), nullable=True)
    estimated_budget = Column(String(100), nullable=True)
    monetization_model = Column(String(150), nullable=True)
    status = Column(String(50), default="PENDING", nullable=False)  # PENDING, IN_PROGRESS, COMPLETED, FAILED

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    report = relationship("ValidationReport", back_populates="idea", uselist=False, cascade="all, delete-orphan")
    search_caches = relationship("SearchResultCache", back_populates="idea", cascade="all, delete-orphan")


class ValidationReport(Base):
    """
    Stores the synthesized multi-agent validation report, scores, and SWOT matrix.
    """
    __tablename__ = "validation_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idea_id = Column(String(36), ForeignKey("startup_ideas.id"), unique=True, nullable=False)

    overall_score = Column(Float, default=0.0)
    feasibility_score = Column(Float, default=0.0)
    market_score = Column(Float, default=0.0)
    uniqueness_score = Column(Float, default=0.0)

    swot_analysis = Column(JSON, nullable=True)  # {strengths: [], weaknesses: [], opportunities: [], threats: []}
    market_sizing = Column(JSON, nullable=True)  # {tam: "", sam: "", som: ""}
    competitor_data = Column(JSON, nullable=True)  # [{name: "", url: "", analysis: ""}]

    summary = Column(Text, nullable=True)
    pdf_report_path = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    idea = relationship("StartupIdea", back_populates="report")
