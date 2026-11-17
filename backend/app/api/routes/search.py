"""
Market Search API Route
=======================
Purpose:
    Exposes direct web search and market research endpoints powered by Tavily Search API.
    Enables ad-hoc competitor discovery and market sentiment exploration.

Milestone Notes:
    - Milestone 1: Route declarations, request validation schemas, and mock responses.
    - Milestone 3: Live Tavily API integration and caching.
"""

import os
import sys

# Ensure backend root directory is in sys.path for direct execution and package imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../../.."))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import APIRouter, status
from app.schemas.response_schema import ApiResponse
from app.schemas.idea_schema import (
    MarketSearchRequest,
    MarketSearchResponse,
    MarketSearchResultItem,
)
from app.core.logging import logger

router = APIRouter(prefix="/search", tags=["Market Search"])


@router.post(
    "/market",
    response_model=ApiResponse[MarketSearchResponse],
    status_code=status.HTTP_200_OK,
    summary="Search Market & Competitor Intelligence",
    description="Runs a targeted web search query to retrieve real-time market data snippets.",
)
def search_market(payload: MarketSearchRequest):
    """
    Executes a web search query for market and competitor intelligence.

    Note:
        Placeholder implementation for Milestone 1. Live Tavily execution will be enabled in Milestone 3.
    """
    logger.info(f"[SearchRoute] Received market search query: '{payload.query}'")

    # Placeholder search results adhering to response schema
    results = [
        MarketSearchResultItem(
            title=f"Industry Trends: {payload.query}",
            url="https://example.com/industry-report",
            content=f"Summary of current trends, major players, and consumer behavior regarding '{payload.query}'.",
            score=0.92,
        ),
        MarketSearchResultItem(
            title=f"Competitive Analysis: {payload.query}",
            url="https://example.com/competitor-analysis",
            content=f"Key market players, valuation multiples, and technological differentiation in this space.",
            score=0.88,
        ),
    ]

    response_data = MarketSearchResponse(
        query=payload.query,
        total_results=len(results),
        results=results,
    )

    return ApiResponse(
        success=True,
        data=response_data,
        message="Market search completed successfully (Milestone 1 skeleton)",
    )


if __name__ == "__main__":
    print("Market Search Route Module Loaded Successfully!")
    test_search = MarketSearchRequest(query="AI Logistics Startups", max_results=2)
    res = search_market(test_search)
    print("Search Results Count:", res.data.total_results)
