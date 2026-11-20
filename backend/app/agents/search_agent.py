"""
Search Agent
============
Purpose:
    Formulates targeted market search queries, calls Tavily Search API,
    and returns verified web intelligence snippets for downstream agents.
"""

import os
import sys
from typing import Any, Dict, List, Optional

# Ensure backend root directory is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../.."))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.services.tavily_service import TavilySearchService, tavily_service
from app.core.logging import logger


class SearchAgent:
    """
    Autonomous agent responsible for querying live web intelligence via Tavily.
    """

    def __init__(self, service: Optional[TavilySearchService] = None):
        self.search_service = service or tavily_service

    def execute(self, startup_name: str, industry: str, problem_or_solution: str) -> List[Dict[str, Any]]:
        """
        Formulates targeted search operators and retrieves real-time web market context.
        """
        query = f"{startup_name} {industry} market trends competitors {problem_or_solution[:60]}".strip()
        logger.info(f"[SearchAgent] Querying Tavily web research with: '{query}'")
        return self.search_service.search(query=query, max_results=5)


# Singleton instance
search_agent = SearchAgent()


if __name__ == "__main__":
    agent = SearchAgent()
    res = agent.execute("PrepAI", "EdTech", "AI interview preparation for students")
    print("SearchAgent Test Results Count:", len(res))
