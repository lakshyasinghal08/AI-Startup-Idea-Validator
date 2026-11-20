"""
Idea & Search Schemas
=====================
Purpose:
    Defines Pydantic models for startup idea submissions, validation results,
    SWOT representations, consulting analysis dossiers, and market search queries.

Milestone Notes:
    - Milestone 1: Data transfer schema declarations with type validation and single-input support.
    - Future Milestones: Will be connected to LLM prompt formatting and agent pipelines.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


class IdeaCreateRequest(BaseModel):
    """
    Schema for incoming startup idea validation requests.
    Supports a single natural language description ('idea') or composite individual fields.
    """
    idea: Optional[str] = Field(
        default=None,
        description="Single natural language startup idea description",
        examples=["I want to build an AI platform that helps students prepare for interviews."],
    )
    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Startup Name or working title",
        examples=["EcoRoute Logistics"],
    )
    problem_statement: Optional[str] = Field(
        default=None,
        description="The core problem the startup intends to solve",
        examples=["Freight carriers lose 15% of annual operating budget on suboptimal fuel routing."],
    )
    solution: Optional[str] = Field(
        default=None,
        description="The proposed product or technological solution",
        examples=["AI-powered smart routing system reducing fuel consumption and emissions."],
    )
    description: Optional[str] = Field(
        default=None,
        description="Composite elevator pitch and problem-solution description",
    )
    target_market: Optional[str] = Field(
        default=None,
        max_length=150,
        description="Industry or market vertical",
        examples=["Logistics & Supply Chain"],
    )
    target_audience: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Target customers or buyer personas",
        examples=["Mid-market trucking fleets and dispatchers"],
    )
    monetization_model: Optional[str] = Field(
        default=None,
        description="Business and revenue model",
        examples=["B2B SaaS monthly recurring subscription"],
    )
    estimated_budget: Optional[str] = Field(
        default=None,
        description="Initial planned budget or capital outlay",
        examples=["$50,000"],
    )
    additional_info: Optional[str] = Field(
        default=None,
        description="Any additional information, traction, or founder context",
    )

    @model_validator(mode="after")
    def sync_fields(self):
        """Ensure title, description, and target_market are populated."""
        raw_text = (self.idea or self.description or "").strip()
        if not raw_text and not self.title and not self.problem_statement:
            raise ValueError("Startup idea description or title must be provided.")

        if not self.description:
            if self.idea:
                self.description = self.idea
            else:
                parts = []
                if self.problem_statement:
                    parts.append(f"Problem: {self.problem_statement}")
                if self.solution:
                    parts.append(f"Solution: {self.solution}")
                if self.additional_info:
                    parts.append(f"Notes: {self.additional_info}")
                self.description = " | ".join(parts) if parts else (self.title or "Startup Idea")

        if not self.title:
            candidate = (self.idea or self.description or "Startup Idea").split(".")[0].strip()
            self.title = candidate[:60] if candidate else "Startup Idea"

        if not self.target_market:
            self.target_market = "Technology & Services"

        return self


class SWOTAnalysis(BaseModel):
    """Structured 4-quadrant SWOT matrix representation."""
    strengths: List[str] = Field(default_factory=list, description="Internal strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Internal weaknesses")
    opportunities: List[str] = Field(default_factory=list, description="External opportunities")
    threats: List[str] = Field(default_factory=list, description="External risks & threats")


class ValidationScores(BaseModel):
    """Quantitative scoring indices (0-100 scale)."""
    overall: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall idea score")
    feasibility: float = Field(default=0.0, ge=0.0, le=100.0, description="Technical and business feasibility")
    market_demand: float = Field(default=0.0, ge=0.0, le=100.0, description="Market demand and sizing potential")
    uniqueness: float = Field(default=0.0, ge=0.0, le=100.0, description="Differentiation against existing solutions")


class IdeaValidationResponse(BaseModel):
    """
    Schema for completed idea validation consulting dossier returned to frontend.
    Formatted similar to top-tier strategy consulting briefs (McKinsey, BCG, Deloitte).
    Contains all 13 consulting sections with full backward compatibility.
    """
    id: str = Field(..., description="Unique validation ID")
    title: str = Field(..., description="Startup idea title")
    status: str = Field(default="completed", description="Analysis execution state")
    scores: ValidationScores = Field(default_factory=ValidationScores)

    # 13 Primary Consulting Report Sections
    executive_summary: Optional[str] = Field(default="", description="1. Executive Summary")
    idea_overview: Optional[str] = Field(default="", description="2. Idea Overview")
    problem_statement: Optional[str] = Field(default="", description="3. Problem Statement")
    proposed_solution: Optional[str] = Field(default="", description="4. Proposed Solution")
    target_customers: Optional[str] = Field(default="", description="5. Target Customers")
    market_analysis: Dict[str, Any] = Field(default_factory=dict, description="6. Market Analysis (TAM/SAM/SOM/CAGR)")
    competitor_analysis: Dict[str, Any] = Field(default_factory=dict, description="7. Competitor Analysis")
    swot_analysis: SWOTAnalysis = Field(default_factory=SWOTAnalysis, description="8. SWOT Analysis")
    business_opportunities: List[str] = Field(default_factory=list, description="9. Business Opportunities")
    potential_risks: List[str] = Field(default_factory=list, description="10. Potential Risks")
    recommendations: List[str] = Field(default_factory=list, description="11. Recommendations")
    overall_validation_score: float = Field(default=0.0, description="12. Overall Validation Score")
    final_conclusion: str = Field(default="", description="13. Final Conclusion")

    # Supporting & Backward-Compatibility Fields
    problem_solution_fit: str = Field(
        default="",
        description="Evaluation of customer pain alignment and solution defensibility",
    )
    market_potential: Dict[str, Any] = Field(
        default_factory=dict,
        description="Market sizing, TAM/SAM/SOM breakdown, and growth CAGR",
    )
    competitors: List[str] = Field(
        default_factory=list,
        description="Identified competitor names",
    )
    swot: SWOTAnalysis = Field(default_factory=SWOTAnalysis)
    business_risks: List[str] = Field(
        default_factory=list,
        description="Operational, technical, regulatory, and market risks",
    )
    growth_opportunities: List[str] = Field(
        default_factory=list,
        description="Scalability levers, geographic expansion, and product expansion",
    )
    summary: str = Field(default="", description="Executive synthesis of the evaluation")
    market_sizing: Dict[str, str] = Field(
        default_factory=dict,
        description="Legacy TAM, SAM, SOM mapping",
    )


class MarketSearchRequest(BaseModel):
    """
    Schema for manual or automated market intelligence web searches.
    """
    query: str = Field(
        ...,
        min_length=3,
        max_length=300,
        description="Keywords or industry query to search for",
    )
    max_results: int = Field(default=5, ge=1, le=10)


class MarketSearchResultItem(BaseModel):
    """Individual web search snippet retrieved."""
    title: str
    url: str
    content: str
    score: float = 0.0


class MarketSearchResponse(BaseModel):
    """Consolidated market search results."""
    query: str
    total_results: int
    results: List[MarketSearchResultItem] = Field(default_factory=list)
