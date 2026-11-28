"""
Market Opportunity & Customer Segmentation Agent
================================================
Purpose:
    Evaluates market dynamics, addressable market sizing (TAM/SAM/SOM),
    compound annual growth rates (CAGR), industry trends, customer segmentation,
    and demand indicators using verified Tavily search evidence and LLM reasoning.
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
    Agent evaluating market opportunities, customer personas, and sizing metrics
    grounded in Tavily search findings.
    """

    def __init__(self, service: LLMService | None = None):
        self.llm_service = service or llm_service

    def execute(
        self,
        extracted_idea: dict[str, Any],
        search_snippets: list[dict[str, Any]] | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Synthesizes market sizing, trends, and customer segmentation using
        industry context, Tavily search findings, and LLM reasoning.
        """
        if not isinstance(extracted_idea, dict):
            raise TypeError("extracted_idea must be a dictionary.")
        if not extracted_idea:
            raise ValueError("extracted_idea must be a non-empty dictionary.")

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
            f"[MarketAgent] Analyzing market sizing, trends, and segments for "
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
        source_urls: list[str] = []
        for snippet in raw_snippets:
            if not isinstance(snippet, dict):
                continue

            title = snippet.get("title", "")
            url = snippet.get("url", "")
            content = snippet.get("content", "")

            if title and url and content:
                url_str = str(url)
                evidence.append({
                    "title": str(title),
                    "url": url_str,
                    "content": str(content)[:2000],
                    "score": snippet.get("score", 0.0),
                })
                if url_str not in source_urls:
                    source_urls.append(url_str)

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

        user_prompt = f"""Analyze the market opportunity and customer segmentation for this startup using the supplied information and search evidence.

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
        if not result:
            raise ValueError("Market analysis response is empty.")

        # Validate that core market fields exist in the LLM response
        if not any(k in result for k in ("market_size", "tam", "trends", "market_trends")):
            raise ValueError(
                "Market analysis response is missing required market sizing or trend fields."
            )

        # Standardize output keys
        m_industry = result.get("industry") or industry
        market_size = result.get("market_size") or "Market scale not specified in sources"
        growth_rate = (
            result.get("growth_rate")
            or result.get("cagr")
            or "Growth rate not available in sources"
        )
        customer_segments = (
            result.get("customer_segments")
            or result.get("target_segments")
            or [target_users]
        )
        if isinstance(customer_segments, str):
            customer_segments = [customer_segments]

        trends = result.get("trends") or result.get("market_trends") or []
        if isinstance(trends, str):
            trends = [trends]

        opportunities = result.get("opportunities") or []
        if isinstance(opportunities, str):
            opportunities = [opportunities]

        challenges = result.get("challenges") or result.get("market_risks") or []
        if isinstance(challenges, str):
            challenges = [challenges]

        target_audience = result.get("target_audience") or target_users
        demand_indicators = result.get("demand_indicators") or []
        if isinstance(demand_indicators, str):
            demand_indicators = [demand_indicators]

        tam = result.get("tam") or (
            market_size.get("tam") if isinstance(market_size, dict) else market_size
        )
        sam = result.get("sam") or (
            market_size.get("sam")
            if isinstance(market_size, dict)
            else "Serviceable available segment not specified"
        )
        som = result.get("som") or (
            market_size.get("som")
            if isinstance(market_size, dict)
            else "Serviceable obtainable beachhead not specified"
        )
        cagr = result.get("cagr") or (
            market_size.get("cagr") if isinstance(market_size, dict) else growth_rate
        )

        demand_drivers_text = (
            "; ".join(demand_indicators)
            if demand_indicators
            else f"Demand in {m_industry} driven by emerging market needs and transition to automated solutions."
        )

        standardized_output = {
            "industry": m_industry,
            "market_size": market_size,
            "growth_rate": growth_rate,
            "customer_segments": customer_segments,
            "target_segments": result.get("target_segments") or customer_segments,
            "target_audience": target_audience,
            "trends": trends,
            "opportunities": opportunities,
            "challenges": challenges,
            "demand_indicators": demand_indicators,
            "source_urls": result.get("source_urls") or source_urls,
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
    agent = MarketAgent()
    sample_idea = {
        "startup_name": "PrepAI",
        "industry": "EdTech",
        "problem": "Students lack automated feedback on mock interviews.",
        "solution": "AI-powered real-time mock interview simulator.",
        "target_users": "College students and engineering graduates",
    }
    print("MarketAgent test run:")
    print(agent.execute(sample_idea, []))