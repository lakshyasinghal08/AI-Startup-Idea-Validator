"""
Startup Idea & Validation Report Domain Models
=============================================
Purpose:
    Defines domain entities for startup idea submissions, validation reports,
    scoring attributes, and SWOT analysis.

Milestone Notes:
    - Milestone 1: In-memory domain entity classes (no active database required).
    - Future Milestones (Milestone 5): Will map to PostgreSQL tables via SQLAlchemy 2.0
      and Alembic schema migrations.
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class StartupIdea:
    """
    Domain entity representing an entrepreneur's submitted startup idea.
    
    Milestone 1: Operates in-memory.
    Milestone 5+: Maps to 'startup_ideas' PostgreSQL table.
    """
    title: str
    description: str
    target_market: str
    id: str = field(default_factory=lambda: f"idea_{uuid.uuid4().hex[:8]}")
    target_audience: str | None = None
    estimated_budget: str | None = None
    monetization_model: str | None = None
    status: str = "PENDING"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to standard Python dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "target_market": self.target_market,
            "target_audience": self.target_audience,
            "estimated_budget": self.estimated_budget,
            "monetization_model": self.monetization_model,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class ValidationReport:
    """
    Domain entity storing synthesized multi-agent validation results and scores.
    
    Milestone 1: Operates in-memory.
    Milestone 5+: Maps to 'validation_reports' PostgreSQL table.
    """
    idea_id: str
    id: str = field(default_factory=lambda: f"report_{uuid.uuid4().hex[:8]}")
    overall_score: float = 0.0
    feasibility_score: float = 0.0
    market_score: float = 0.0
    uniqueness_score: float = 0.0
    swot_analysis: dict[str, list[str]] = field(default_factory=dict)
    market_sizing: dict[str, str] = field(default_factory=dict)
    competitor_data: list[str] = field(default_factory=list)
    summary: str | None = None
    pdf_report_path: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to standard Python dictionary."""
        return {
            "id": self.id,
            "idea_id": self.idea_id,
            "overall_score": self.overall_score,
            "feasibility_score": self.feasibility_score,
            "market_score": self.market_score,
            "uniqueness_score": self.uniqueness_score,
            "swot_analysis": self.swot_analysis,
            "market_sizing": self.market_sizing,
            "competitor_data": self.competitor_data,
            "summary": self.summary,
            "pdf_report_path": self.pdf_report_path,
            "created_at": self.created_at.isoformat(),
        }


if __name__ == "__main__":
    test_idea = StartupIdea(
        title="EcoRoute AI",
        description="Smart routing for fleet carbon footprint reduction",
        target_market="Logistics",
    )
    print("StartupIdea Domain Model initialized:", test_idea.id, test_idea.title)
