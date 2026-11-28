"""
Market Opportunity & Customer Segmentation Agent
================================================
Purpose:
    Analyzes industry size (TAM/SAM/SOM & CAGR), market trends, demand drivers,
    and target customer segments using Tavily search evidence and LLM analysis.
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


class MarketAgent:
    """Agent for evidence-based market opportunity and customer segmentation analysis."""

    def __init__(self, service: LLMService | None = None):
        self.llm_service = service or llm_service

    def execute(
        self,
        extracted_idea: dict[str, Any],
        search_snippets: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Analyzes market size, industry trends, and target customer segments
        using structured startup information and web search evidence.
        """
        if not isinstance(extracted_idea, dict) or not extracted_idea:
            raise ValueError("extracted_idea must be a non-empty dictionary.")

        startup_name = extracted_idea.get("startup_name", "Startup")
        industry = extracted_idea.get("industry", "Technology")

        logger.info(
            f"[MarketAgent] Analyzing market opportunity and customer segments for "
            f"'{startup_name}' in '{industry}'"
        )

        # Prepare clean search evidence
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
            logger.warning("[MarketAgent] No search evidence available.")

        system_prompt = """
You are an experienced startup market research and customer segmentation analyst.

Your task is to evaluate the market opportunity, industry size, key trends,
and target customer segments using the supplied startup information and web search evidence.

IMPORTANT RULES:
1. Ground all market size figures, CAGR numbers, and trend claims in the supplied search evidence.
2. Do NOT fabricate specific dollar figures, growth rates, or statistics that are not in the evidence.
3. If a specific metric (such as TAM, SAM, SOM, or CAGR) is unavailable in the sources, write "Not available in sources".
4. Include source URLs only when they appear in the supplied evidence.
5. Define clear, actionable target customer segments aligned with the startup's problem and solution.
6. Return valid JSON only, without Markdown formatting.

Use this exact JSON structure:

{
    "industry": "Industry name",
    "market_size": {
        "tam": "Evidence-based TAM or Not available in sources",
        "sam": "Evidence-based SAM or Not available in sources",
        "som": "Evidence-based SOM or Not available in sources",
        "cagr": "Evidence-based CAGR or Not available in sources"
    },
    "market_trends": [
        {
            "trend": "Key industry trend supported by evidence",
            "impact": "How this trend affects the startup opportunity",
            "source_urls": ["Source URL"]
        }
    ],
    "demand_drivers": ["Primary factor driving customer demand"],
    "target_segments": [
        {
            "segment_name": "Name of customer segment",
            "profile": "Demographics or firmographics of this segment",
            "pain_points": ["Specific pain point this segment faces"],
            "willingness_to_pay": "Low / Medium / High with brief rationale",
            "priority": "Primary / Secondary"
        }
    ],
    "market_opportunity_summary": "Concise synthesis of the overall market opportunity",
    "market_risks": ["Key market adoption or timing risk"],
    "source_urls": ["Source URL"]
}

If no search evidence is supplied, state "Not available in sources" for market size metrics,
return an empty market_trends list, and explain the evidence limitation in market_opportunity_summary.
"""

        user_prompt = f"""
Analyze the market opportunity and customer segmentation for this startup.

STARTUP INFORMATION:
{json.dumps(extracted_idea, indent=2, ensure_ascii=False)}

TAVILY SEARCH EVIDENCE:
{json.dumps(evidence, indent=2, ensure_ascii=False)}

Provide evidence-backed industry sizing, trends, demand drivers, and target customer segments.
"""

        result = self.llm_service.generate_structured_json_sync(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )

        if not isinstance(result, dict):
            raise ValueError("Market analysis returned an invalid response.")

        required_keys = {"industry", "market_size", "market_trends", "target_segments"}
        missing_keys = required_keys - result.keys()
        if missing_keys:
            raise ValueError(
                f"Market analysis response is missing required keys: {sorted(missing_keys)}"
            )

        logger.info(
            f"[MarketAgent] Market and segmentation analysis completed for '{startup_name}'."
        )

        return result


# Singleton instance
market_agent = MarketAgent()


if __name__ == "__main__":
    agent = MarketAgent()

    sample_idea = {
        "startup_name": "PrepAI",
        "industry": "EdTech",
        "problem_statement": "Students struggle with technical interview preparation.",
        "proposed_solution": "AI-powered mock interview and feedback platform.",
        "target_customers": "College students and recent graduates",
    }

    print(agent.execute(sample_idea, []))