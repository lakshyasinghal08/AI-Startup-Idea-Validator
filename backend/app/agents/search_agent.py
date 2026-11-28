
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
        startup_name: str | dict[str, Any],
        industry: str | None = None,
        problem_or_solution: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute targeted web research and return genuine Tavily results.
        Accepts either explicit parameters or a structured Idea JSON dictionary.
        """
        if isinstance(startup_name, dict):
            idea_dict = startup_name
            name = (
                idea_dict.get("startup_name")
                or idea_dict.get("title")
                or "Startup Idea"
            )
            ind = (
                idea_dict.get("industry")
                or idea_dict.get("target_market")
                or "Technology & Services"
            )
            prob = (
                idea_dict.get("problem")
                or idea_dict.get("problem_statement")
                or idea_dict.get("solution")
                or idea_dict.get("proposed_solution")
                or ""
            )
        else:
            name = startup_name
            ind = industry or ""
            prob = problem_or_solution or ""

        if not name or not str(name).strip():
            raise ValueError("Startup name cannot be empty.")

        if not ind or not str(ind).strip():
            raise ValueError("Industry cannot be empty.")

        if not prob or not str(prob).strip():
            raise ValueError("Problem or solution cannot be empty.")

        queries = self._generate_queries(
            str(name).strip(),
            str(ind).strip(),
            str(prob).strip(),
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
                    max_results=5,
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
                    f"Market research failed while executing search query {index}: {exc!s}"
                ) from exc

        logger.info(
            f"[SearchAgent] Research completed. "
            f"Unique results collected: {len(all_results)}"
        )

        return all_results

    def search_idea(
        self,
        idea: dict[str, Any] | str,
    ) -> dict[str, Any]:
        """
        Standardized entrypoint returning structured search output:
        {
            "search_results": list[dict],
            "sources": list[dict],
            "urls": list[str]
        }
        """
        results = self.execute(idea)
        sources = [
            {"title": r.get("title", ""), "url": r.get("url", "")}
            for r in results
            if r.get("url")
        ]
        urls = [r.get("url", "") for r in results if r.get("url")]

        return {
            "search_results": results,
            "sources": sources,
            "urls": urls,
        }


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
