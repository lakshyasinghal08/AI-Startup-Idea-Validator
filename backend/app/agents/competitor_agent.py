"""
Competitor Intelligence Agent
=============================
Purpose:
    Identifies direct and indirect competitors, benchmarks their strengths,
    weaknesses, features, and pricing models, and discovers market gaps and defensible
    moats using verified Tavily search evidence and Groq LLM reasoning.
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
        Analyzes competitors using startup information and verified Tavily search evidence.
        Uses real Groq LLM reasoning without fabrication.
        """
        if not isinstance(extracted_idea, dict):
            raise TypeError("extracted_idea must be a dictionary.")

        startup_name = (
            extracted_idea.get("startup_name")
            or extracted_idea.get("title")
            or "Startup Venture"
        )
        industry = (
            extracted_idea.get("industry")
            or extracted_idea.get("target_market")
            or "Technology & Services"
        )
        problem = (
            extracted_idea.get("problem")
            or extracted_idea.get("problem_statement")
            or ""
        )
        solution = (
            extracted_idea.get("solution")
            or extracted_idea.get("proposed_solution")
            or ""
        )

        logger.info(
            f"[CompetitorAgent] Analyzing competitors for "
            f"'{startup_name}' in '{industry}'"
        )

        # Unpack snippets if wrapped in a dict
        raw_snippets: list[Any] = []
        if isinstance(search_snippets, dict):
            raw_snippets = search_snippets.get("search_results", [])
        elif isinstance(search_snippets, list):
            raw_snippets = search_snippets

        # Prepare relevant search evidence
        evidence: list[dict[str, Any]] = []
        for snippet in raw_snippets:
            if not isinstance(snippet, dict):
                continue

            title = snippet.get("title", "")
            url = snippet.get("url", "")
            content = snippet.get("content", "")

            if title and url and content:
                evidence.append({
                    "title": str(title),
                    "url": str(url),
                    "content": str(content)[:2000],
                    "score": snippet.get("score", 0.0),
                })

        if not evidence:
            logger.warning("[CompetitorAgent] No search evidence available for competitor analysis.")

        system_prompt = COMPETITOR_ANALYSIS_PROMPT

        startup_context = {
            "startup_name": startup_name,
            "industry": industry,
            "problem": problem,
            "solution": solution,
        }

        user_prompt = f"""Analyze the competitive landscape for this startup.

STARTUP INFORMATION:
{json.dumps(startup_context, indent=2, ensure_ascii=False)}

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
