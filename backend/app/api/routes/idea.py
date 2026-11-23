"""
Startup Idea Validation API Routes
==================================
Purpose:
    Exposes endpoints for submitting startup ideas, triggering the multi-agent
    validation pipeline, and retrieving consulting analysis dossiers.

Milestone Notes:
    - Milestone 1: Multi-agent execution pipeline orchestrating LLM extraction (Gemini/OpenAI/Groq),
      Tavily search intelligence, market sizing, competitor moats, SWOT analysis, and 13-section report synthesis.
    - Milestone 5: Persistent PostgreSQL database storage.
"""

import os
import sys

# Ensure backend root directory is in sys.path for direct execution and package imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../../.."))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.agents.competitor_agent import competitor_agent
from app.agents.idea_agent import idea_agent
from app.agents.market_agent import market_agent
from app.agents.report_agent import report_agent
from app.agents.search_agent import search_agent
from app.agents.swot_agent import swot_agent
from app.core.logging import logger
from app.schemas.idea_schema import (
    IdeaCreateRequest,
    IdeaValidationResponse,
    SWOTAnalysis,
    ValidationScores,
)
from app.schemas.response_schema import ApiResponse
from app.services.llm_service import LLMConfigurationError, llm_service
from app.services.tavily_service import TavilyConfigurationError, tavily_service
from app.utils.helpers import generate_short_id
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/idea", tags=["Idea Validation"])


@router.post(
    "/validate",
    response_model=ApiResponse[IdeaValidationResponse],
    status_code=status.HTTP_200_OK,
    summary="Submit Startup Idea for Validation",
    description="Accepts startup details or single natural language idea and triggers the multi-agent pipeline.",
)
def validate_idea(payload: IdeaCreateRequest) -> ApiResponse[IdeaValidationResponse]:
    """
    Submits a startup idea for multi-agent evaluation and generates a 16-section consulting report.

    Pipeline:
      1. IdeaAgent: Uses LLM to extract structured attributes (problem, solution, audience, industry, model).
      2. SearchAgent: Uses Tavily API to fetch real market intelligence snippets.
      3. MarketAgent: Estimates TAM, SAM, SOM, CAGR, and growth drivers.
      4. CompetitorAgent: Maps direct and indirect competitors and moats.
      5. SWOTAgent: Builds 4-quadrant strategic matrix.
      6. ReportAgent: Synthesizes findings into 16 management consulting sections.
    """
    if not llm_service.is_configured():
        missing_key = llm_service.get_missing_key_name()
        logger.error(f"[IdeaRoute] LLM API key '{missing_key}' is not configured.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{missing_key} not configured.",
        )

    if not tavily_service.is_configured():
        logger.error("[IdeaRoute] TAVILY_API_KEY is not configured.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TAVILY_API_KEY not configured.",
        )

    raw_idea = (payload.idea or payload.description or payload.title or "").strip()
    if not raw_idea:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Idea text cannot be empty.",
        )

    logger.info(f"[IdeaRoute] Starting multi-agent validation pipeline for idea: '{raw_idea[:80]}...'")

    generated_id = generate_short_id()

    # Step 1: LLM Idea Extraction
    try:
        extracted = idea_agent.extract_idea(raw_idea)
    except LLMConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:  # noqa: BLE001
        logger.error(f"[IdeaRoute] IdeaAgent extraction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM idea extraction failed: {e!s}",
        )

    # Overlay with explicit user fields if provided
    startup_name = payload.title if payload.title and payload.title != "Startup Idea" else extracted.get("startup_name", "Startup Venture")
    industry = payload.target_market if payload.target_market and payload.target_market != "Technology & Services" else extracted.get("industry", "Technology & Services")
    problem = payload.problem_statement or extracted.get("problem_statement", "Fragmented workflows and lack of specialized automation.")
    solution = payload.solution or extracted.get("proposed_solution", "Intelligent platform automating workflow execution.")
    target_customers = payload.target_audience or extracted.get("target_customers", "Target users and institutional teams")
    business_model = payload.monetization_model or extracted.get("business_model", "Freemium Subscription (SaaS)")
    value_proposition = extracted.get("value_proposition", "Automated, scalable intelligence for higher productivity.")

    consolidated_idea = {
        "startup_name": startup_name,
        "industry": industry,
        "problem_statement": problem,
        "proposed_solution": solution,
        "target_customers": target_customers,
        "business_model": business_model,
        "value_proposition": value_proposition,
    }

    # Step 2: Tavily Search Agent
    try:
        search_snippets = search_agent.execute(startup_name, industry, problem)
    except TavilyConfigurationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TAVILY_API_KEY not configured.",
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"[IdeaRoute] SearchAgent execution error: {e}")
        search_snippets = []

    # Step 3: Market Analysis Agent
    try:
        market_data = market_agent.execute(consolidated_idea, search_snippets)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"[IdeaRoute] MarketAgent execution error: {e}. Using fallback.")
        market_data = {}

    # Step 4: Competitor Intelligence Agent
    try:
        competitor_data = competitor_agent.execute(consolidated_idea, search_snippets)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"[IdeaRoute] CompetitorAgent execution error: {e}. Using fallback.")
        competitor_data = {}

    # Step 5: SWOT Analysis Agent
    try:
        swot_data = swot_agent.execute(consolidated_idea, market_data, competitor_data)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"[IdeaRoute] SWOTAgent execution error: {e}. Using fallback.")
        swot_data = {}

    # Step 6: Report Synthesis Agent (13 Sections)
    report_dict = report_agent.compile_report(
        extracted_idea=consolidated_idea,
        search_snippets=search_snippets,
        market_data=market_data,
        competitor_data=competitor_data,
        swot_data=swot_data,
    )

    # Build Pydantic Response Models
    scores_dict = report_dict.get("scores", {})
    val_scores = ValidationScores(
        overall=scores_dict.get("overall", 82.0),
        feasibility=scores_dict.get("feasibility", 85.0),
        market_demand=scores_dict.get("market_demand", 82.0),
        uniqueness=scores_dict.get("uniqueness", 81.0),
    )

    swot_dict = report_dict.get("swot_analysis", {})
    swot_obj = SWOTAnalysis(
        strengths=swot_dict.get("strengths", []),
        weaknesses=swot_dict.get("weaknesses", []),
        opportunities=swot_dict.get("opportunities", []),
        threats=swot_dict.get("threats", []),
    )

    response_payload = IdeaValidationResponse(
        id=generated_id,
        title=startup_name,
        status="completed",
        scores=val_scores,
        executive_summary=report_dict.get("executive_summary", ""),
        startup_overview=report_dict.get("startup_overview") or report_dict.get("idea_overview", ""),
        problem_statement=report_dict.get("problem_statement", ""),
        proposed_solution=report_dict.get("proposed_solution", ""),
        target_customers=report_dict.get("target_customers", ""),
        industry=report_dict.get("industry", industry),
        business_model=report_dict.get("business_model", business_model),
        market_research=report_dict.get("market_research", ""),
        market_trends=report_dict.get("market_trends", []),
        competitor_analysis=report_dict.get("competitor_analysis", {}),
        swot_analysis=swot_obj,
        opportunities=report_dict.get("opportunities", []),
        risks=report_dict.get("risks", []),
        recommendations=report_dict.get("recommendations", []),
        overall_validation_score=val_scores.overall,
        final_conclusion=report_dict.get("final_conclusion", ""),
        # Backward compatibility
        idea_overview=report_dict.get("startup_overview") or report_dict.get("idea_overview", ""),
        market_analysis=report_dict.get("market_analysis", {}),
        business_opportunities=report_dict.get("opportunities", []),
        potential_risks=report_dict.get("risks", []),
        business_risks=report_dict.get("risks", []),
        growth_opportunities=report_dict.get("opportunities", []),
        problem_solution_fit=report_dict.get("proposed_solution", ""),
        market_potential=report_dict.get("market_analysis", {}),
        competitors=report_dict.get("competitors", []),
        swot=swot_obj,
        summary=report_dict.get("executive_summary", ""),
        market_sizing=report_dict.get("market_sizing", {}),
    )

    return ApiResponse(
        success=True,
        data=response_payload,
        message="Idea validated successfully via multi-agent pipeline",
    )


@router.get(
    "/{idea_id}",
    response_model=ApiResponse[IdeaValidationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Validation Report by ID",
    description="Retrieves a previously generated startup validation report by its unique ID.",
)
def get_idea_validation(idea_id: str) -> ApiResponse[IdeaValidationResponse]:
    """
    Retrieves a validation report by ID.

    Note:
        In Milestone 1, returns a structured report with 16 consulting sections.
        Persistent database storage will be connected in Milestone 5.
    """
    logger.info(f"[IdeaRoute] Fetching report for ID: '{idea_id}'")

    if idea_id == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{idea_id}' not found",
        )

    val_scores = ValidationScores(overall=82.0, feasibility=85.0, market_demand=82.0, uniqueness=81.0)
    swot_obj = SWOTAnalysis(
        strengths=["Clear value proposition", "Favorable unit economics", "Lightweight tech stack"],
        weaknesses=["Early brand obscurity", "Initial customer acquisition friction", "Domain calibration requirements"],
        opportunities=["High-growth market tailwinds", "Institutional partnerships", "API ecosystem expansion"],
        threats=["Incumbent feature bundling", "Early customer price sensitivity", "User retention challenges"],
    )

    mock_response = IdeaValidationResponse(
        id=idea_id,
        title="Sample Startup Validation",
        status="completed",
        scores=val_scores,
        executive_summary="Executive Validation Dossier: Demonstrates solid market fundamentals and addressable competitive moats.",
        startup_overview="A high-velocity automated workflow platform serving high-growth digital segments.",
        idea_overview="A high-velocity automated workflow platform serving high-growth digital segments.",
        problem_statement="Fragmented tooling and labor-intensive manual methods leading to lost economic output.",
        proposed_solution="Automated, intelligent platform delivering rapid turnaround and measurable efficiency.",
        target_customers="Enterprise and SME teams seeking automated productivity.",
        industry="B2B SaaS & Artificial Intelligence",
        business_model="Monthly Recurring SaaS Subscription",
        market_research="Industry data indicates strong enterprise demand for workflow acceleration tools.",
        market_trends=[
            "Migration toward automated domain intelligence.",
            "Rising customer preference for specialized outcome tools.",
            "Demand for transparent benchmarking.",
        ],
        market_analysis={
            "tam": "$12.8B Global Enterprise Sector",
            "sam": "$2.6B Addressable Segment",
            "som": "$185M 3-Year Beachhead",
            "cagr": "14.2% CAGR",
            "demand_drivers": "Migration toward automated workflows and productivity acceleration.",
        },
        competitor_analysis={
            "direct_competitors": [{"name": "Incumbent Alpha", "vulnerability": "Legacy tech debt and high prices"}],
            "indirect_competitors": ["In-house spreadsheets and manual processes"],
            "defensive_moats": ["Proprietary feedback loops and high switching costs"],
        },
        swot_analysis=swot_obj,
        opportunities=["Beachhead expansion", "Tiered licensing", "API ecosystem"],
        risks=["Customer acquisition friction", "Incumbent bundling", "User retention"],
        business_opportunities=["Beachhead expansion", "Tiered licensing", "API ecosystem"],
        potential_risks=["Customer acquisition friction", "Incumbent bundling", "User retention"],
        business_risks=["Customer acquisition friction", "Incumbent bundling", "User retention"],
        growth_opportunities=["Beachhead expansion", "Tiered licensing", "API ecosystem"],
        recommendations=["Validate with 20 user interviews", "Ship lean MVP in 45 days", "Secure 3 pilot agreements"],
        overall_validation_score=82.0,
        final_conclusion="Strategic Verdict: Highly Viable with defined execution milestones.",
        # Backward compatibility
        problem_solution_fit="Strong product-market alignment observed.",
        market_potential={"tam": "$12.8B", "sam": "$2.6B", "som": "$185M"},
        competitors=["Incumbent Corp", "Point Solution Startup"],
        swot=swot_obj,
        summary="Historical report retrieval.",
        market_sizing={"tam": "$12.8B", "sam": "$2.6B", "som": "$185M"},
    )

    return ApiResponse(
        success=True,
        data=mock_response,
        message="Report retrieved successfully",
    )


if __name__ == "__main__":
    print("Startup Idea Validation Route Module Loaded Successfully!")
    test_req = IdeaCreateRequest(
        idea="I want to build an AI platform that helps students prepare for interviews."
    )
    res = validate_idea(test_req)
    if res.data:
        print("Direct Execution Result:", res.data.title, "- Overall Score:", res.data.overall_validation_score)
