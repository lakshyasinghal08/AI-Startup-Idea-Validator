
"""
Tavily Search Service
=====================
Purpose:
    Connects to the Tavily Search API and returns genuine web
    intelligence results for downstream agents.
"""

import os
import sys
from typing import Any
from urllib.parse import urlparse

import httpx

# Ensure backend root directory is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../.."))

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.config import settings
from app.core.logging import logger


class TavilySearchError(Exception):
    """Raised when Tavily search fails."""


class TavilyConfigurationError(TavilySearchError):
    """Raised when Tavily configuration is missing or invalid."""


class TavilySearchService:
    """Service responsible for live Tavily web searches."""

    API_URL = "https://api.tavily.com/search"

    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY

    def is_configured(self) -> bool:
        """Check whether a usable Tavily API key is configured."""

        return bool(
            self.api_key
            and self.api_key.startswith("tvly-")
            and "your-tavily-api-key-here" not in self.api_key
        )

    def _validate_results(
        self,
        results: Any
    ) -> list[dict[str, Any]]:
        """Validate and normalize genuine Tavily results."""

        if not isinstance(results, list):
            raise TavilySearchError(
                "Tavily returned an invalid results structure."
            )

        normalized_results = []

        for item in results:
            if not isinstance(item, dict):
                continue

            title = item.get("title")
            url = item.get("url")
            content = item.get("content")
            raw_score = item.get("score")

            if not isinstance(title, str) or not title.strip():
                continue
            if not isinstance(url, str) or not url.strip():
                continue
            if not isinstance(content, str) or not content.strip():
                continue

            parsed_url = urlparse(url)
            if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
                continue

            if raw_score is None:
                continue
            try:
                score_val = float(raw_score)
            except (TypeError, ValueError):
                continue

            normalized_results.append({
                "title": title.strip(),
                "url": url.strip(),
                "content": content.strip(),
                "score": score_val,
            })

        return normalized_results

    def search(
        self,
        query: str,
        search_depth: str = "advanced",
        max_results: int = 5
    ) -> list[dict[str, Any]]:
        """
        Execute a live Tavily search.

        Returns only genuine results received from Tavily.
        Never generates fabricated fallback results.
        """

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if search_depth not in ("basic", "advanced"):
            raise ValueError(
                "search_depth must be 'basic' or 'advanced'."
            )

        if not isinstance(max_results, int) or not 1 <= max_results <= 20:
            raise ValueError(
                "max_results must be between 1 and 20."
            )

        if not self.is_configured():
            raise TavilyConfigurationError(
                "TAVILY_API_KEY not configured."
            )

        payload = {
            "api_key": self.api_key,
            "query": query.strip(),
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": False,
        }

        logger.info("[TavilyService] Starting live search.")

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.API_URL,
                    json=payload,
                )

                response.raise_for_status()
                data = response.json()

            results = self._validate_results(
                data.get("results", [])
            )

            logger.info(
                f"[TavilyService] HTTP REST returned "
                f"{len(results)} genuine results."
            )

            return results

        except httpx.HTTPStatusError as exc:
            logger.error(
                f"[TavilyService] HTTP error: {exc.response.status_code}"
            )
            raise TavilySearchError(
                "Tavily rejected the search request."
            ) from exc

        except httpx.RequestError as exc:
            logger.error(
                f"[TavilyService] Network request failed: {exc}"
            )
            raise TavilySearchError(
                "Unable to connect to Tavily."
            ) from exc

        except ValueError as exc:
            logger.error(
                f"[TavilyService] Invalid response: {exc}"
            )
            raise TavilySearchError(
                "Tavily returned an invalid response."
            ) from exc


# Singleton instance
tavily_service = TavilySearchService()


if __name__ == "__main__":
    try:
        results = tavily_service.search(
            "AI interview preparation platforms competitors",
            max_results=3,
        )

        print("Results:", len(results))

        for result in results:
            print("\nTitle:", result["title"])
            print("URL:", result["url"])
            print("Score:", result["score"])

    except TavilySearchError as exc:
        print("Search failed:", exc)
