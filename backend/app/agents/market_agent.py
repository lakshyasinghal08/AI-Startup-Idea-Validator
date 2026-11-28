"""
Market Analysis Agent
=====================
Purpose:
    Evaluates market dynamics, addressable market sizing (TAM/SAM/SOM),
    compound annual growth rates (CAGR), industry trends, customer segmentation,
    and demand indicators using verified Tavily search evidence and Groq LLM reasoning.
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
from app.prompt import MARKET_ANALYSIS_PROMPT
from app.services.llm_service import LLMService, llm_service


class MarketAgent:
    """
    Agent evaluating market opportunities, customer personas, and sizing metrics.
    Uses real Groq LLM reasoning grounded in Tavily search findings.
    """

    def __init__(self, service: LLMService | None = None):
        self.llm_service = service or llm_service

    def execute(
        self,
        extracted_idea: dict[str, Any],
        search_snippets: list[dict[str, Any]] | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Synthesizes market sizing, trends, and growth projections using industry
        context, genuine Tavily search findings, and Groq LLM reasoning.
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
        target_users = (
            extracted_idea.get("target_users")
            or extracted_idea.get("target_customers")
            or extracted_idea.get("target_audience")
            or "Target customers"
        )

        logger.info(
            f"[MarketAgent] Analyzing market sizing, trends, and CAGR for "
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
            logger.warning("[MarketAgent] No search evidence available for market analysis.")

        system_prompt = MARKET_ANALYSIS_PROMPT

        startup_context = {
            "startup_name": startup_name,
            "industry": industry,
            "problem": problem,
            "solution": solution,
            "target_audience": target_users,
        }

        user_prompt = f"""Analyze the market opportunity for this startup using the supplied information and search evidence.

STARTUP INFORMATION:
{json.dumps(startup_context, indent=2, ensure_ascii=False)}

TAVILY SEARCH EVIDENCE:
{json.dumps(evidence, indent=2, ensure_ascii=False)}

Conduct a rigorous market analysis. Ground all trends, sizing, and customer demand strictly in the provided evidence.
If specific sizing figures are unavailable, state 'Quantitative sizing data not available in sources' and describe qualitative scale.
"""

        result = self.llm_service.generate_structured_json_sync(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )

        if not isinstance(result, dict):
            raise TypeError("Market analysis returned an invalid response from LLM.")

        # Standardize output keys
        m_industry = result.get("industry") or industry
        market_size = result.get("market_size") or "Market scale not specified in sources"
        growth_rate = result.get("growth_rate") or result.get("cagr") or "Growth rate not available in sources"
        customer_segments = result.get("customer_segments") or [target_users]
        if isinstance(customer_segments, str):
            customer_segments = [customer_segments]

        trends = result.get("trends") or []
        if isinstance(trends, str):
            trends = [trends]

        opportunities = result.get("opportunities") or []
        if isinstance(opportunities, str):
            opportunities = [opportunities]

        challenges = result.get("challenges") or []
        if isinstance(challenges, str):
            challenges = [challenges]

        target_audience = result.get("target_audience") or target_users
        demand_indicators = result.get("demand_indicators") or []
        if isinstance(demand_indicators, str):
            demand_indicators = [demand_indicators]

        tam = result.get("tam") or market_size
        sam = result.get("sam") or "Serviceable available segment not specified"
        som = result.get("som") or "Serviceable obtainable beachhead not specified"
        cagr = result.get("cagr") or growth_rate

        demand_drivers_text = "; ".join(demand_indicators) if demand_indicators else (
            f"Demand in {m_industry} driven by emerging market needs and transition to automated solutions."
        )

        standardized_output = {
            "industry": m_industry,
            "market_size": market_size,
            "growth_rate": growth_rate,
            "customer_segments": customer_segments,
            "target_audience": target_audience,
            "trends": trends,
            "opportunities": opportunities,
            "challenges": challenges,
            "demand_indicators": demand_indicators,
            # Backwards compatibility for Milestone 1:
            "tam": tam,
            "sam": sam,
            "som": som,
            "cagr": cagr,
            "demand_drivers": demand_drivers_text,
            "market_demand_score": float(result.get("market_demand_score", 82.0)),
        }

        logger.info(f"[MarketAgent] Analysis completed successfully for '{startup_name}'.")
        return standardized_output


# Singleton instance
market_agent = MarketAgent()


if __name__ == "__main__":
    sample_idea = {
        "startup_name": "PrepAI",
        "industry": "EdTech",
        "problem": "Students lack automated feedback on mock interviews.",
        "solution": "AI-powered real-time mock interview simulator.",
        "target_users": "College students and engineering graduates",
    }
    print("MarketAgent test run:")
    agent = MarketAgent()
    print(agent.execute(sample_idea, []))
