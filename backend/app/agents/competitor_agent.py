"""
Competitor Intelligence Agent
=============================
Purpose:
    Identifies direct and indirect competitors, compares their strengths
    and weaknesses, and discovers market gaps using Tavily evidence
    and LLM analysis.
"""

import json
import os
import sys
from typing import Any

# Ensure backend root directory is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../.."))

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.logging import logger
from app.prompt import COMPETITOR_ANALYSIS_PROMPT
from app.services.llm_service import LLMService, llm_service


class CompetitorAgent:
    """Agent for evidence-based competitor discovery, benchmarking, and moat identification."""

    def __init__(self, service: LLMService | None = None):
        self.llm_service = service or llm_service

    def execute(
        self,
        extracted_idea: dict[str, Any],
        search_snippets: list[dict[str, Any]] | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze competitors using startup information and Tavily evidence.
        """
        # Validate startup idea
        if not isinstance(extracted_idea, dict):
            raise TypeError("extracted_idea must be a dictionary.")

        startup_name = extracted_idea.get("startup_name", "Startup")
        industry = extracted_idea.get("industry", "Technology")

        logger.info(
            f"[CompetitorAgent] Analyzing competitors for "
            f"'{startup_name}' in '{industry}'"
        )

        # Normalize dictionary-wrapped search results
        if isinstance(search_snippets, dict):
            for key in ("results", "search_results", "data"):
                if isinstance(search_snippets.get(key), list):
                    search_snippets = search_snippets[key]
                    break
            else:
                # Allow a single search-result dictionary
                if all(
                    key in search_snippets
                    for key in ("title", "url", "content")
                ):
                    search_snippets = [search_snippets]
                else:
                    search_snippets = []

        if search_snippets is None:
            search_snippets = []

        if not isinstance(search_snippets, list):
            raise TypeError(
                "search_snippets must be a list or dictionary."
            )

        # Prepare relevant search evidence
        evidence = []

        for snippet in search_snippets:
            if not isinstance(snippet, dict):
                continue

            title = snippet.get("title", "")
            url = snippet.get("url", "")
            content = snippet.get("content", "")

            if not isinstance(content, str):
                continue

            if title and url and content:
                evidence.append({
                    "title": str(title),
                    "url": str(url),
                    "content": str(content)[:2000],
                    "score": snippet.get("score", 0.0),
                })

        if not evidence:
            logger.warning(
                "[CompetitorAgent] No search evidence available."
            )

        system_prompt = """
You are an experienced startup competitive intelligence analyst.

Your task is to identify direct and indirect competitors, compare their
offerings, analyze market gaps, and identify differentiation opportunities
using the supplied startup information and web search evidence.

IMPORTANT RULES:
1. Use only the supplied search evidence for competitor-specific facts.
2. Never invent competitor names, websites, features, pricing, or statistics.
3. Classify competitors as direct or indirect based on their relevance.
4. If information is unavailable, write "Not available in sources".
5. Include source URLs only when they appear in the supplied evidence.
6. Do not treat the startup being evaluated as its own competitor.
7. Compare competitors using the same relevant criteria wherever possible.
8. Do not assume a competitor lacks a feature just because it is not
   mentioned in the supplied search results.
9. Distinguish verified facts from potential market opportunities.
10. Base market gaps on evidence of unmet customer needs or limitations.
11. Return valid JSON only, without Markdown formatting.

Use this exact JSON structure:

{
    "direct_competitors": [
        {
            "name": "Competitor name",
            "strengths": ["Evidence-based strength"],
            "weaknesses_or_gaps": ["Evidence-based weakness or Not available in sources"],
            "source_urls": ["Source URL"]
        }
    ],
    "indirect_competitors": [
        {
            "name": "Competitor name",
            "strengths": ["Evidence-based strength"],
            "weaknesses_or_gaps": ["Evidence-based weakness or Not available in sources"],
            "source_urls": ["Source URL"]
        }
    ],
    "feature_comparison": [
        {
            "competitor_name": "Competitor name",
            "key_features": ["Features supported by evidence"],
            "target_customers": "Identified customer segment or Not available in sources",
            "pricing_model": "Pricing information or Not available in sources",
            "evidence_summary": "Brief evidence-based summary",
            "source_urls": ["Source URL"]
        }
    ],
    "comparison_summary": "Compare the competitors and explain their relative strengths and positioning.",
    "market_gaps": [
        {
            "gap": "Identified market gap",
            "unmet_customer_need": "Customer need that is not adequately addressed",
            "opportunity": "How the startup could address this gap",
            "supporting_evidence": "Evidence from the supplied search results",
            "source_urls": ["Source URL"]
        }
    ],
    "competitive_risks": ["Evidence-based competitive risk"],
    "differentiation_opportunities": ["Realistic opportunity for differentiation"],
    "defensive_moats": ["Potential defensible advantage"]
}

If the evidence does not identify competitors, return empty competitor
lists and explain the limitation in comparison_summary.

If the evidence is insufficient to establish a market gap, return an
empty market_gaps list rather than inventing one.

Ensure all competitor-specific claims are traceable to the supplied
search evidence.
"""

        user_prompt = f"""Analyze the competitive landscape for this startup.

STARTUP INFORMATION:
{json.dumps(extracted_idea, indent=2, ensure_ascii=False)}

TAVILY SEARCH EVIDENCE:
{json.dumps(evidence, indent=2, ensure_ascii=False)}

Identify relevant direct and indirect competitors and compare them.
Ensure every competitor-specific claim, feature, and pricing detail is supported by the evidence.
If pricing is not stated in the sources, write 'Not available in sources'.
"""

        result = self.llm_service.generate_structured_json_sync(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )

        if not isinstance(result, dict):
            raise TypeError("Competitor analysis returned an invalid response from LLM.")

        # Standardize competitor output structure
        direct_competitors = result.get("direct_competitors") or []
        if not isinstance(direct_competitors, list):
            direct_competitors = []

        indirect_competitors = result.get("indirect_competitors") or []
        if not isinstance(indirect_competitors, list):
            indirect_competitors = []

        strengths = result.get("strengths") or []
        if isinstance(strengths, str):
            strengths = [strengths]

        weaknesses = result.get("weaknesses") or []
        if isinstance(weaknesses, str):
            weaknesses = [weaknesses]

        market_gaps = result.get("market_gaps") or []
        if isinstance(market_gaps, str):
            market_gaps = [market_gaps]

        risks = result.get("risks") or result.get("competitive_risks") or []
        if isinstance(risks, str):
            risks = [risks]

        unique_opportunities = (
            result.get("unique_opportunities")
            or result.get("differentiation_opportunities")
            or []
        )
        if isinstance(unique_opportunities, str):
            unique_opportunities = [unique_opportunities]

        comparison_summary = (
            result.get("comparison_summary")
            or f"Competitive benchmarking completed for {startup_name} in {industry}."
        )

        defensive_moats = result.get("defensive_moats") or []
        if isinstance(defensive_moats, str):
            defensive_moats = [defensive_moats]

        standardized_output = {
            "direct_competitors": direct_competitors,
            "indirect_competitors": indirect_competitors,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "market_gaps": market_gaps,
            "risks": risks,
            "unique_opportunities": unique_opportunities,
            "comparison_summary": comparison_summary,
            "competitive_risks": risks,
            "differentiation_opportunities": unique_opportunities,
            "defensive_moats": defensive_moats,
        }

        logger.info(f"[CompetitorAgent] Analysis completed successfully for '{startup_name}'.")
        return standardized_output


# Singleton instance
competitor_agent = CompetitorAgent()


if __name__ == "__main__":
    sample_idea = {
        "startup_name": "PrepAI",
        "industry": "EdTech",
        "problem_statement": "Students struggle with interview preparation.",
        "proposed_solution": "AI-powered interview preparation platform.",
        "target_customers": "College students and graduates",
    }
    agent = CompetitorAgent()
    print("CompetitorAgent test run:")
    print(agent.execute(sample_idea, []))
