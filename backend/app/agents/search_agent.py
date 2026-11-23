
"""
Search Agent
============
Purpose:
    Formulates targeted market research queries, calls Tavily Search API,
    and returns genuine web intelligence snippets for downstream agents.
"""

import os
import sys
from typing import Any

# Ensure backend root directory is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../.."))

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.logging import logger
from app.services.tavily_service import TavilySearchService, tavily_service


class SearchAgent:
    """
    Agent responsible for collecting live market intelligence through Tavily.
    """

    def __init__(self, service: TavilySearchService | None = None):
        self.search_service = service or tavily_service

    def _generate_queries(
        self,
        startup_name: str,
        industry: str,
        problem_or_solution: str
    ) -> list[str]:
        """
        Generate targeted queries covering different market research areas.
        """

        context = (
            f'"{startup_name}" {industry} {problem_or_solution}'
        ).strip()

        queries = [
            f"{context} market trends industry developments",
            f"{context} market demand growth opportunities",
            f"{context} competitors competing products alternative solutions",
            f"{context} customer problems pain points unmet needs",
            f"{context} industry gaps emerging opportunities",
        ]

        return queries

    def execute(
        self,
        startup_name: str,
        industry: str,
        problem_or_solution: str
    ) -> list[dict[str, Any]]:
        """
        Execute targeted web research and return genuine Tavily results.
        """

        if not startup_name or not startup_name.strip():
            raise ValueError("Startup name cannot be empty.")

        if not industry or not industry.strip():
            raise ValueError("Industry cannot be empty.")

        if not problem_or_solution or not problem_or_solution.strip():
            raise ValueError("Problem or solution cannot be empty.")

        queries = self._generate_queries(
            startup_name.strip(),
            industry.strip(),
            problem_or_solution.strip()
        )

        all_results: list[dict[str, Any]] = []
        seen_urls = set()

        for index, query in enumerate(queries, start=1):
            logger.info(
                f"[SearchAgent] Executing research query "
                f"{index}/{len(queries)}: {query}"
            )

            try:
                results = self.search_service.search(
                    query=query,
                    max_results=5
                )

                if not results:
                    logger.warning(
                        f"[SearchAgent] No results returned for query {index}."
                    )
                    continue

                for result in results:
                    url = result.get("url")

                    if not isinstance(url, str) or not url.strip():
                        continue

                    normalized_url = url.strip().rstrip("/").lower()

                    if normalized_url in seen_urls:
                        continue

                    seen_urls.add(normalized_url)
                    all_results.append(result)

            except Exception as exc:
                logger.exception(
                    "[SearchAgent] Search query %s failed.", index
                )
                raise RuntimeError(
                    f"Market research failed while executing search query {index}. "
                    "Please retry when the search service is available."
                ) from exc

        logger.info(
            f"[SearchAgent] Research completed. "
            f"Unique results collected: {len(all_results)}"
        )

        return all_results


# Singleton instance
search_agent = SearchAgent()


if __name__ == "__main__":
    agent = SearchAgent()

    try:
        results = agent.execute(
            "PrepAI",
            "EdTech",
            "AI interview preparation for students"
        )

        print("SearchAgent Test Results Count:", len(results))

        for result in results:
            print("\nTitle:", result.get("title"))
            print("URL:", result.get("url"))
            print("Score:", result.get("score"))

    except Exception as exc:  # noqa: BLE001
        print("SearchAgent test failed:", exc)
