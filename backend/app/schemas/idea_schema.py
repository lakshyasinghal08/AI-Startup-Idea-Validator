"""
Idea & Search Schemas
=====================
Purpose:
    Defines Pydantic models for startup idea submissions, validation results,
    SWOT representations, and market search queries.

Milestone Notes:
    - Milestone 1: Data transfer schema declarations with type validation.
    - Future Milestones: Will be connected to LLM prompt formatting and agent pipelines.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class IdeaCreateRequest(BaseModel):
    """
    Schema for incoming startup idea validation requests.
    """
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Name or working title of the startup project",
        examples=["EcoRoute Logistics"],
    )
    description: str = Field(
        ...,
        min_length=15,
        max_length=5000,
        description="Detailed elevator pitch and problem-solution description",
        examples=["AI-powered smart routing system reducing fuel consumption for freight carriers."],
    )
    target_market: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Primary industry or business sector",
        examples=["Logistics & Supply Chain"],
    )
    target_audience: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Primary customer persona or demographic segment",
        examples=["B2B Trucking Fleets and Dispatchers"],
    )
    estimated_budget: Optional[str] = Field(
        default=None,
        description="Initial planned budget or capital outlay",
        examples=["$25,000"],
    )
    monetization_model: Optional[str] = Field(
        default=None,
        description="Intended revenue model",
        examples=["B2B SaaS monthly recurring subscription"],
    )


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
    Schema for completed idea validation dossier returned to frontend.
    """
    id: str = Field(..., description="Unique validation ID")
    title: str = Field(..., description="Startup idea title")
    status: str = Field(default="completed", description="Analysis execution state")
    scores: ValidationScores = Field(default_factory=ValidationScores)
    swot: SWOTAnalysis = Field(default_factory=SWOTAnalysis)
    summary: str = Field(default="", description="Executive synthesis of the evaluation")
    competitors: List[str] = Field(default_factory=list, description="Identified competitor names")
    market_sizing: Dict[str, str] = Field(
        default_factory=dict,
        description="TAM, SAM, SOM estimates",
    )


class MarketSearchRequest(BaseModel):
    """
    Schema for manual or automated market intelligence web searches.
    """
    query: str = Field(
        ...,
        min_length=3,
        max_length=300,
        description="Search query to run against real-time web indexes",
        examples=["Electric vehicle battery swapping competitors in Europe"],
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum search results to retrieve",
    )


class MarketSearchResultItem(BaseModel):
    """Single search result item returned from search service."""
    title: str
    url: str
    content: str
    score: Optional[float] = None


class MarketSearchResponse(BaseModel):
    """Collection of search results."""
    query: str
    total_results: int
    results: List[MarketSearchResultItem] = Field(default_factory=list)
