
"""
Competitor Intelligence Agent
=============================
Purpose:
    Identifies direct and indirect competitors, compares their strengths
    and weaknesses, and discovers differentiation opportunities using
    Tavily search evidence and LLM analysis.
"""

import os
import sys
import json
from typing import Any

# Ensure backend root directory is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../.."))

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.logging import logger
from app.services.llm_service import LLMService, llm_service


class CompetitorAgent:
    """Agent for evidence-based competitor discovery and comparison."""

    def __init__(self, service: LLMService | None = None):
        self.llm_service = service or llm_service

    def execute(
        self,
        extracted_idea: dict[str, Any],
        search_snippets: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Analyzes competitors using startup information and web search evidence.
        """

        startup_name = extracted_idea.get("startup_name", "Startup")
        industry = extracted_idea.get("industry", "Technology")

        logger.info(
            f"[CompetitorAgent] Analyzing competitors for "
            f"'{startup_name}' in '{industry}'"
        )

        # Prepare relevant search evidence
        evidence = []

        for snippet in (search_snippets or []):
            if not isinstance(snippet, dict):
                continue

            title = snippet.get("title", "")
            url = snippet.get("url", "")
            content = snippet.get("content", "")

            if title and url and content:
                evidence.append({
                    "title": title,
                    "url": url,
                    "content": content[:2000],
                    "score": snippet.get("score", 0.0),
                })

        if not evidence:
            logger.warning(
                "[CompetitorAgent] No search evidence available."
            )

        system_prompt = """
You are an experienced startup competitive intelligence analyst.

Your task is to identify and compare competitors using the supplied
startup information and web search evidence.

IMPORTANT RULES:
1. Use only the supplied search evidence for competitor-specific facts.
2. Do not invent competitor names, websites, pricing, features, or statistics.
3. Classify competitors as direct or indirect based on their relevance.
4. If a detail is unavailable, write "Not available in sources".
5. Include source URLs only when they appear in the supplied evidence.
6. Do not treat the startup being evaluated as its own competitor.
7. Identify realistic differentiation opportunities based on the evidence.
8. Return valid JSON only, without Markdown formatting.

Use this exact JSON structure:

{
    "direct_competitors": [
        {
            "name": "Competitor name",
            "strengths": ["Strength supported by evidence"],
            "weaknesses_or_gaps": ["Evidence-based gap or Not available in sources"],
            "source_urls": ["Source URL"]
        }
    ],
    "indirect_competitors": [
        {
            "name": "Competitor name",
            "strengths": ["Strength supported by evidence"],
            "weaknesses_or_gaps": ["Evidence-based gap or Not available in sources"],
            "source_urls": ["Source URL"]
        }
    ],
    "comparison_summary": "Summary of the competitive landscape",
    "competitive_risks": ["Competitive risk"],
    "differentiation_opportunities": ["Opportunity for differentiation"],
    "defensive_moats": ["Potential defensible advantage"]
}

If the evidence does not identify competitors, return empty competitor
lists and explain the limitation in comparison_summary.
"""

        user_prompt = f"""
Analyze the competitive landscape for this startup.

STARTUP INFORMATION:
{json.dumps(extracted_idea, indent=2, ensure_ascii=False)}

TAVILY SEARCH EVIDENCE:
{json.dumps(evidence, indent=2, ensure_ascii=False)}

Identify relevant direct and indirect competitors and compare them.
Ensure every competitor-specific claim is supported by the evidence.
"""

        # Generate structured competitor analysis using the LLM
        result = self.llm_service.generate_structured_json_sync(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )

        if not isinstance(result, dict):
            raise ValueError(
                "Competitor analysis returned an invalid response."
            )

        logger.info(
            f"[CompetitorAgent] Analysis completed for '{startup_name}'."
        )

        return result


# Singleton instance
competitor_agent = CompetitorAgent()


if __name__ == "__main__":
    agent = CompetitorAgent()

    sample_idea = {
        "startup_name": "PrepAI",
        "industry": "EdTech",
        "problem_statement": "Students struggle with interview preparation.",
        "proposed_solution": "AI-powered interview preparation platform.",
        "target_customers": "College students and graduates",
    }

    print(agent.execute(sample_idea, []))
