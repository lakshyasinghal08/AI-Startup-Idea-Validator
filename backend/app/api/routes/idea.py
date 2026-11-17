"""
Startup Idea Validation API Routes
==================================
Purpose:
    Exposes endpoints for submitting startup ideas, triggering the multi-agent
    validation pipeline, and retrieving historical analysis dossiers.

Milestone Notes:
    - Milestone 1: Route declarations, request validation schemas, and mock responses.
    - Milestone 2 & 4: Link to multi-agent orchestrator execution and persistent storage.
"""

import os
import sys

# Ensure backend root directory is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../../.."))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import APIRouter, HTTPException, status
from app.schemas.response_schema import ApiResponse
from app.schemas.idea_schema import (
    IdeaCreateRequest,
    IdeaValidationResponse,
    ValidationScores,
    SWOTAnalysis,
)
from app.utils.helpers import generate_short_id
from app.core.logging import logger

router = APIRouter(prefix="/idea", tags=["Idea Validation"])


@router.post(
    "/validate",
    response_model=ApiResponse[IdeaValidationResponse],
    status_code=status.HTTP_200_OK,
    summary="Submit Startup Idea for Validation",
    description="Accepts startup details and triggers the multi-agent market validation workflow.",
)
def validate_idea(payload: IdeaCreateRequest):
    """
    Submits a startup idea for multi-agent evaluation.

    Note:
        In Milestone 1, this returns a structured baseline response adhering to the
        contract schema. Multi-agent execution will be connected in subsequent milestones.
    """
    logger.info(f"[IdeaRoute] Received validation request for idea: '{payload.title}'")

    generated_id = generate_short_id()

    # Baseline response matching future multi-agent schema
    mock_response = IdeaValidationResponse(
        id=generated_id,
        title=payload.title,
        status="completed",
        scores=ValidationScores(
            overall=82.0,
            feasibility=85.0,
            market_demand=80.0,
            uniqueness=81.0,
        ),
        swot=SWOTAnalysis(
            strengths=[
                f"Strong initial focus on {payload.target_market}",
                "Clear value proposition defined",
            ],
            weaknesses=[
                "High initial customer acquisition costs common in this sector",
                "Requires early strategic partnerships",
            ],
            opportunities=[
                "Expanding addressable market through AI automation",
                "Adjacent cross-sell opportunities in enterprise segments",
            ],
            threats=[
                "Rapidly evolving competitive landscape",
                "Potential regulatory scrutiny depending on jurisdiction",
            ],
        ),
        summary=(
            f"Preliminary validation for '{payload.title}': The concept demonstrates viable product-market "
            f"fit indicators within the {payload.target_market} space."
        ),
        competitors=["Competitor One (Market Leader)", "Competitor Two (Emerging Challenger)"],
        market_sizing={
            "tam": "$12.8B global sector size",
            "sam": "$2.5B serviceable market",
            "som": "$180M initial beachhead",
        },
    )

    return ApiResponse(
        success=True,
        data=mock_response,
        message="Idea validation completed successfully (Milestone 1 skeleton)",
    )


@router.get(
    "/{idea_id}",
    response_model=ApiResponse[IdeaValidationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Validation Report by ID",
    description="Retrieves a previously generated startup validation report by its unique ID.",
)
def get_idea_validation(idea_id: str):
    """
    Retrieves a validation report by ID.

    Note:
        Placeholder endpoint for Milestone 1. Database lookups will be connected in Milestone 5.
    """
    logger.info(f"[IdeaRoute] Fetching report for ID: '{idea_id}' (placeholder)")

    if idea_id == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{idea_id}' not found",
        )

    mock_response = IdeaValidationResponse(
        id=idea_id,
        title="Sample Startup Validation",
        status="completed",
        scores=ValidationScores(overall=78.0, feasibility=80.0, market_demand=75.0, uniqueness=79.0),
        swot=SWOTAnalysis(
            strengths=["Established domain expertise"],
            weaknesses=["Resource constraints"],
            opportunities=["Emerging tech adoption"],
            threats=["Macroeconomic volatility"],
        ),
        summary="Historical report retrieval placeholder.",
    )

    return ApiResponse(
        success=True,
        data=mock_response,
        message="Report retrieved successfully",
    )


if __name__ == "__main__":
    print("Startup Idea Validation Route Module Loaded Successfully!")
    test_req = IdeaCreateRequest(
        title="Test Idea",
        description="Testing direct idea route execution.",
        target_market="Tech",
    )
    res = validate_idea(test_req)
    print("Direct Execution Result:", res.data.title, "- Status:", res.data.status)
