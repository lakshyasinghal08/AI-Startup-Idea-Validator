"""
Search Result Cache Domain Model
================================
Purpose:
    Domain entity for caching web search results and competitor snippets.

Milestone Notes:
    - Milestone 1: In-memory domain entity class (no active database required).
    - Future Milestones (Milestone 5): Will map to 'search_result_caches' PostgreSQL table
      with TTL caching and semantic indexing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


@dataclass
class SearchResultCache:
    """
    Domain entity for cached search results and market intelligence snippets.
    
    Milestone 1: Operates in-memory.
    Milestone 5+: Maps to 'search_result_caches' PostgreSQL table.
    """
    query: str
    snippet: str
    id: str = field(default_factory=lambda: f"search_{uuid.uuid4().hex[:8]}")
    idea_id: Optional[str] = None
    source_url: Optional[str] = None
    title: Optional[str] = None
    relevance_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to standard Python dictionary."""
        return {
            "id": self.id,
            "idea_id": self.idea_id,
            "query": self.query,
            "source_url": self.source_url,
            "title": self.title,
            "snippet": self.snippet,
            "relevance_score": self.relevance_score,
            "created_at": self.created_at.isoformat(),
        }


if __name__ == "__main__":
    cache = SearchResultCache(
        query="SaaS Logistics market size",
        snippet="Global freight logistics is growing at 8% CAGR.",
        title="Freight Analysis 2026",
    )
    print("SearchResultCache Domain Model initialized:", cache.id, cache.query)
