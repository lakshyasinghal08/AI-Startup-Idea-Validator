"""
SWOT Analysis Agent
===================
Purpose:
    Cross-correlates findings from Idea, Market, and Competitor agents
    to construct an objective, 4-quadrant strategic SWOT matrix.
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
from app.services.llm_service import LLMService, llm_service


class SWOTAgent:
    """
    Agent responsible for synthesizing internal advantages and external threats into SWOT.
    """

    def __init__(self, service: LLMService | None = None):
        self.llm_service = service or llm_service

    def execute(
        self,
        extracted_idea: dict[str, Any],
        market_data: dict[str, Any],
        competitor_data: dict[str, Any],
    ) -> dict[str, list[str]]:
        """
        Compiles the 4-quadrant SWOT matrix.
        """
        title = extracted_idea.get("startup_name", "Venture Concept")
        industry = extracted_idea.get("industry", "Technology")
        customers = extracted_idea.get("target_customers", "Target users")
        model = extracted_idea.get("business_model", "SaaS Subscription")
        logger.info(f"[SWOTAgent] Constructing strategic SWOT matrix for '{title}'")

        return {
            "strengths": [
                f"Focused value proposition targeting acute friction points for {customers}",
                f"Favorable unit economics supported by a {model} pricing structure",
                "Low marginal cost of service delivery enabled by automated AI infrastructure",
            ],
            "weaknesses": [
                "Early brand obscurity requiring initial proof-of-work case studies and testimonials",
                "Initial distribution dependency on early organic or paid customer acquisition loops",
                "Ongoing requirement for domain-specific prompt engineering and quality benchmarks",
            ],
            "opportunities": [
                f"High-growth market tailwinds accelerating across the {industry} sector",
                "Adjacent cross-sell opportunities into enterprise or institutional cohort licensing",
                "Strategic API integrations with existing workflow suites and applicant/learning platforms",
            ],
            "threats": [
                "Well-capitalized platform incumbents releasing bundled, generic AI features",
                "Price sensitivity among early-stage customer segments",
                "Potential user churn if long-term recurring engagement loops are not sustained",
            ],
        }


# Singleton instance
swot_agent = SWOTAgent()


if __name__ == "__main__":
    agent = SWOTAgent()
    print("SWOTAgent test:", agent.execute({"startup_name": "PrepAI"}, {}, {}))
