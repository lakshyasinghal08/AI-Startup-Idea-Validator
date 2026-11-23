"""
Idea & Search Schemas
=====================
Purpose:
    Defines Pydantic models for startup idea submissions, validation results,
    SWOT representations, consulting analysis dossiers, and market search queries.

Milestone Notes:
    - Milestone 1: Data transfer schema declarations with type validation and single-input support.
    - Future Milestones: Will be connected to persistent storage and PDF exports.
"""

from typing import Any

from pydantic import BaseModel, Field, model_validator


class IdeaCreateRequest(BaseModel):
    """
    Schema for incoming startup idea validation requests.
    Supports a single natural language description ('idea') or composite individual fields.
    """
    idea: str | None = Field(
        default=None,
        description="Single natural language startup idea description",
        examples=["I want to build an AI platform that helps students prepare for interviews."],
    )
    title: str | None = Field(
        default=None,
        max_length=200,
        description="Startup Name or working title",
        examples=["EcoRoute Logistics"],
    )
    problem_statement: str | None = Field(
        default=None,
        description="The core problem the startup intends to solve",
        examples=["Freight carriers lose 15% of annual operating budget on suboptimal fuel routing."],
    )
    solution: str | None = Field(
        default=None,
        description="The proposed product or technological solution",
        examples=["AI-powered smart routing system reducing fuel consumption and emissions."],
    )
    description: str | None = Field(
        default=None,
        description="Composite elevator pitch and problem-solution description",
    )
    target_market: str | None = Field(
        default=None,
        max_length=150,
        description="Industry or market vertical",
        examples=["Logistics & Supply Chain"],
    )
    target_audience: str | None = Field(
        default=None,
        max_length=255,
        description="Target customers or buyer personas",
        examples=["Mid-market trucking fleets and dispatchers"],
    )
    monetization_model: str | None = Field(
        default=None,
        description="Business and revenue model",
        examples=["B2B SaaS monthly recurring subscription"],
    )
    estimated_budget: str | None = Field(
        default=None,
        description="Initial planned budget or capital outlay",
        examples=["$50,000"],
    )
    additional_info: str | None = Field(
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
    strengths: list[str] = Field(default_factory=list, description="Internal strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Internal weaknesses")
    opportunities: list[str] = Field(default_factory=list, description="External opportunities")
    threats: list[str] = Field(default_factory=list, description="External risks & threats")


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
    Contains all 16 consulting sections with full backward compatibility.
    """
    id: str = Field(..., description="Unique validation ID")
    title: str = Field(..., description="Startup idea title")
    status: str = Field(default="completed", description="Analysis execution state")
    scores: ValidationScores = Field(default_factory=ValidationScores)

    # 16 Primary Consulting Report Sections
    executive_summary: str | None = Field(default="", description="1. Executive Summary")
    startup_overview: str | None = Field(default="", description="2. Startup Overview")
    problem_statement: str | None = Field(default="", description="3. Problem Statement")
    proposed_solution: str | None = Field(default="", description="4. Proposed Solution")
    target_customers: str | None = Field(default="", description="5. Target Customers")
    industry: str | None = Field(default="", description="6. Industry")
    business_model: str | None = Field(default="", description="7. Business Model")
    market_research: str | None = Field(default="", description="8. Market Research")
    market_trends: list[str] = Field(default_factory=list, description="9. Market Trends")
    competitor_analysis: dict[str, Any] = Field(default_factory=dict, description="10. Competitor Analysis")
    swot_analysis: SWOTAnalysis = Field(default_factory=SWOTAnalysis, description="11. SWOT Analysis")
    opportunities: list[str] = Field(default_factory=list, description="12. Opportunities")
    risks: list[str] = Field(default_factory=list, description="13. Risks")
    recommendations: list[str] = Field(default_factory=list, description="14. Recommendations")
    overall_validation_score: float = Field(default=0.0, description="15. Overall Validation Score")
    final_conclusion: str = Field(default="", description="16. Final Conclusion")

    # Supporting & Backward-Compatibility Fields
    idea_overview: str | None = Field(default="", description="Alias for Startup Overview")
    market_analysis: dict[str, Any] = Field(default_factory=dict, description="Market Analysis")
    problem_solution_fit: str = Field(
        default="",
        description="Evaluation of customer pain alignment and solution defensibility",
    )
    market_potential: dict[str, Any] = Field(
        default_factory=dict,
        description="Market sizing, TAM/SAM/SOM breakdown, and growth CAGR",
    )
    competitors: list[str] = Field(
        default_factory=list,
        description="Identified competitor names",
    )
    swot: SWOTAnalysis = Field(default_factory=SWOTAnalysis)
    business_opportunities: list[str] = Field(default_factory=list, description="Alias for Opportunities")
    business_risks: list[str] = Field(default_factory=list, description="Alias for Risks")
    potential_risks: list[str] = Field(default_factory=list, description="Alias for Risks")
    growth_opportunities: list[str] = Field(default_factory=list, description="Alias for Opportunities")
    summary: str = Field(default="", description="Executive synthesis of the evaluation")
    market_sizing: dict[str, str] = Field(
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
    results: list[MarketSearchResultItem] = Field(default_factory=list)
