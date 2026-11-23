"""
Market Search API Route
=======================
Exposes live web search and market research endpoints powered by
the Tavily Search API.
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
from app.services.tavily_service import (
    TavilyConfigurationError,
    TavilySearchError,
    TavilyConfigurationError,
    tavily_service,
)
from app.core.logging import logger


router = APIRouter(prefix="/search", tags=["Market Search"])


@router.post(
    "/market",
    response_model=ApiResponse[MarketSearchResponse],
    status_code=status.HTTP_200_OK,
    summary="Search Market & Competitor Intelligence",
    description="Runs a live Tavily search for market intelligence.",
)
def search_market(payload: MarketSearchRequest):
    """Execute a live Tavily search and return genuine results."""

    logger.info(
        "[SearchRoute] Received market search query: '%s'",
        payload.query,
    )

    try:
        raw_results = tavily_service.search(
            query=payload.query,
            max_results=payload.max_results,
        )

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

    except TavilyConfigurationError as exc:
        logger.error("[SearchRoute] Tavily configuration error: %s", exc)

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except TavilySearchError as exc:
        logger.error("[SearchRoute] Tavily search failed: %s", exc)

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("[SearchRoute] Unexpected search error: %s", exc)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during market search.",
        ) from exc
