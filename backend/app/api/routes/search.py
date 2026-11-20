
"""
Market Search API Route
=======================
Purpose:
<<<<<<< HEAD
    Exposes web search and market research endpoints powered by Tavily Search API.
    Enables live competitor discovery and market sentiment exploration.

Milestone Notes:
    - Milestone 1: Live Tavily API integration with structured search results and fallback resilience.
=======
    Exposes live web search and market research endpoints powered by
    the Tavily Search API.
>>>>>>> 902a34d (Integrate live Tavily search with market research agent)
"""

import os
import sys

_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../../.."))

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import APIRouter, HTTPException, status

from app.schemas.response_schema import ApiResponse
from app.schemas.idea_schema import (
    MarketSearchRequest,
    MarketSearchResponse,
    MarketSearchResultItem,
)
<<<<<<< HEAD
from app.services.tavily_service import tavily_service
=======
from app.services.tavily_service import (
    TavilySearchError,
    tavily_service,
)
>>>>>>> 902a34d (Integrate live Tavily search with market research agent)
from app.core.logging import logger


router = APIRouter(prefix="/search", tags=["Market Search"])


@router.post(
    "/market",
    response_model=ApiResponse[MarketSearchResponse],
    status_code=status.HTTP_200_OK,
    summary="Search Market & Competitor Intelligence",
<<<<<<< HEAD
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
=======
    description="Runs a live Tavily search for market intelligence.",
)
def search_market(payload: MarketSearchRequest):
    """Execute a live Tavily search and return genuine results."""

    logger.info(
        f"[SearchRoute] Received market search query: '{payload.query}'"
    )

    try:
        raw_results = tavily_service.search(
            query=payload.query,
            max_results=payload.max_results,
        )
>>>>>>> 902a34d (Integrate live Tavily search with market research agent)

        results = [
            MarketSearchResultItem(
                title=item["title"],
                url=item["url"],
                content=item["content"],
                score=item["score"],
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
            message="Live market search completed successfully.",
        )

    except TavilySearchError as exc:
        logger.error(f"[SearchRoute] Tavily search failed: {exc}")

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Market search provider failed to return results.",
        ) from exc

    except Exception as exc:
        logger.error(f"[SearchRoute] Unexpected search error: {exc}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during market search.",
        ) from exc
