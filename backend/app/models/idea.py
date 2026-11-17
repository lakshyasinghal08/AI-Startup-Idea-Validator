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

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


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
    target_audience: Optional[str] = None
    estimated_budget: Optional[str] = None
    monetization_model: Optional[str] = None
    status: str = "PENDING"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
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
    swot_analysis: Dict[str, List[str]] = field(default_factory=dict)
    market_sizing: Dict[str, str] = field(default_factory=dict)
    competitor_data: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    pdf_report_path: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
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
