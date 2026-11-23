
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

_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../../.."))

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.logging import logger
from app.schemas.idea_schema import (
    MarketSearchRequest,
    MarketSearchResponse,
    MarketSearchResultItem,
)
from app.schemas.response_schema import ApiResponse
from app.services.tavily_service import (
    TavilyConfigurationError,
    TavilySearchError,
    tavily_service,
)
from fastapi import APIRouter, HTTPException, status

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
    When TAVILY_API_KEY is missing, returns clear HTTP error with meaningful JSON.
    Never returns fabricated fallback data.
    """
    logger.info(f"[SearchRoute] Received market search query: '{payload.query}'")

    if not tavily_service.is_configured():
        logger.error("[SearchRoute] TAVILY_API_KEY is not configured.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TAVILY_API_KEY not configured.",
        )

    try:
        raw_results = tavily_service.search(
            query=payload.query,
            max_results=payload.max_results,
        )
    except TavilyConfigurationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TAVILY_API_KEY not configured.",
        )
    except TavilySearchError as exc:
        logger.error(f"[SearchRoute] Tavily search error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Tavily search failed: {exc!s}",
        )
    except Exception as exc:  # noqa: BLE001
        logger.error(f"[SearchRoute] Unexpected search error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search execution failed: {exc!s}",
        )

    results = [
        MarketSearchResultItem(
            title=item.get("title", ""),
            url=item.get("url", ""),
            content=item.get("content", ""),
            score=float(item.get("score", 0.0)),
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
    if res.data:
        print("Search Results Count:", res.data.total_results)
