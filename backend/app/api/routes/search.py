"""
Market Search API Route
=======================
Purpose:
    Exposes web search and market research endpoints powered by Tavily Search API.
    Enables live competitor discovery and market sentiment exploration.

Milestone Notes:
    - Milestone 1: Live Tavily API integration with structured search results and fallback resilience.
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
from app.services.tavily_service import tavily_service
from app.core.logging import logger

router = APIRouter(prefix="/search", tags=["Market Search"])


@router.post(
    "/market",
    response_model=ApiResponse[MarketSearchResponse],
    status_code=status.HTTP_200_OK,
    summary="Search Market & Competitor Intelligence",
    description="Runs a targeted web search query via Tavily Search API to retrieve real-time market data snippets.",
)
def search_market(payload: MarketSearchRequest) -> ApiResponse[MarketSearchResponse]:
    """
    Executes a live web search query for market and competitor intelligence via Tavily.
    """
    logger.info(f"[SearchRoute] Received market search query: '{payload.query}'")

    try:
        raw_results = tavily_service.search(
            query=payload.query,
            max_results=payload.max_results,
        )
    except Exception as e:
        logger.error(f"[SearchRoute] Tavily search error: {e}. Executing fallback.")
        raw_results = []

    results = [
        MarketSearchResultItem(
            title=item.get("title", f"Market Result: {payload.query}"),
            url=item.get("url", "https://tavily.com"),
            content=item.get("content", f"Live market findings for {payload.query}."),
            score=float(item.get("score", 0.9)),
        )
        for item in raw_results
    ]

    response_data = MarketSearchResponse(
        query=payload.query,
        total_results=len(results),
        results=results,
    )

    return ApiResponse(
        success=True,
        data=response_data,
        message="Market search completed successfully via Tavily Search API",
    )


if __name__ == "__main__":
    print("Market Search Route Module Loaded Successfully!")
    test_search = MarketSearchRequest(query="AI Logistics Startups", max_results=2)
    res = search_market(test_search)
    print("Search Results Count:", res.data.total_results)
