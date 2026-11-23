"""
Idea Validation & Extraction Agent
==================================
Purpose:
    Extracts structured startup attributes from raw idea text and evaluates
    the startup's problem-solution fit, feasibility, uniqueness, and potential
    using the configured LLM service.
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


class IdeaAgent:
    """
    Agent responsible for extracting startup details and evaluating
    startup ideas using the configured LLM service.
    """

    def __init__(self, service: LLMService | None = None):
        self.llm_service = service or llm_service

    def extract_idea(self, raw_idea: str) -> dict[str, Any]:
        """Extract structured startup details from raw user input."""
        logger.info("[IdeaAgent] Extracting startup information via LLM")
        return self.llm_service.extract_startup_details(raw_idea)

    @staticmethod
    def _normalize_score(value: Any) -> float | None:
        """Convert a valid score to a number between 0 and 100."""
        try:
            score = float(value)
            if 0 <= score <= 100:
                return round(score, 2)
        except (TypeError, ValueError):
            pass

        return None

    def evaluate(self, extracted_data: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate a startup idea using LLM-generated structured feedback.

        Scores are generated dynamically based on the supplied startup details.
        """
        logger.info(
            "[IdeaAgent] Generating AI-based startup evaluation for '%s'",
            extracted_data.get("startup_name", "Venture"),
        )

        system_prompt = """
You are an experienced startup analyst, product strategist, and business evaluator.

Evaluate startup ideas critically, objectively, and based only on the information
provided. Do not automatically give high scores or assume that an idea is viable.

Evaluate these dimensions:
1. feasibility_score: Technical, operational, and financial feasibility of building
   and launching an initial product.
2. uniqueness_score: Differentiation from existing solutions and defensibility.
3. problem_clarity_score: How clearly the idea identifies a real problem and
   affected users.
4. market_potential_score: Potential demand, target market, scalability, and
   opportunity.
5. solution_defensibility_score: Barriers to imitation, proprietary advantages,
   and long-term competitive advantage.

Scores must be integers from 0 to 100.
Use conservative scores when evidence is limited.
Do not invent market research, customer validation, competitor data, or facts.

Return ONLY a valid JSON object with exactly these fields:
{
    "problem_solution_fit": "Detailed analysis of how well the solution addresses the problem",
    "feasibility_score": 0,
    "uniqueness_score": 0,
    "problem_clarity_score": 0,
    "market_potential_score": 0,
    "solution_defensibility_score": 0,
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "recommendations": ["recommendation 1", "recommendation 2"]
}
"""

        user_prompt = f"""
Evaluate the following startup idea.

Startup details:
{extracted_data}

Assess the idea independently. Scores must reflect the actual idea, not generic
startup assumptions. Explain weaknesses and provide actionable recommendations.
"""

        try:
            result = self.llm_service.generate_structured_json_sync(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
            )

            if not isinstance(result, dict):
                raise TypeError("LLM returned an invalid evaluation format")

            score_fields = [
                "feasibility_score",
                "uniqueness_score",
                "problem_clarity_score",
                "market_potential_score",
                "solution_defensibility_score",
            ]

            normalized_scores = {
                field: self._normalize_score(result.get(field))
                for field in score_fields
            }

            missing_scores = [
                field for field, value in normalized_scores.items()
                if value is None
            ]

            if missing_scores:
                logger.warning(
                    "[IdeaAgent] Missing or invalid evaluation scores: %s",
                    missing_scores,
                )

            evaluation = {
                "problem_solution_fit": str(
                    result.get("problem_solution_fit", "")
                ),
                **normalized_scores,
                "strengths": result.get("strengths", []),
                "weaknesses": result.get("weaknesses", []),
                "recommendations": result.get("recommendations", []),
            }

            return evaluation

        except Exception as exc:  # noqa: BLE001
            logger.exception("[IdeaAgent] AI evaluation failed: %s", exc)

            return {
                "problem_solution_fit": (
                    "AI evaluation could not be completed. "
                    "Please retry when the LLM service is available."
                ),
                "feasibility_score": None,
                "uniqueness_score": None,
                "problem_clarity_score": None,
                "market_potential_score": None,
                "solution_defensibility_score": None,
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
            }

    def execute_sync(
        self, idea_data: dict[str, Any] | str
    ) -> dict[str, Any]:
        """
        Synchronously extracts and evaluates a startup idea.
        Accepts raw text or structured user input.
        """
        if isinstance(idea_data, str):
            desc = idea_data
            extracted = self.extract_idea(idea_data)

            title = extracted.get("startup_name")
            target_market = extracted.get("industry")

        else:
            title = idea_data.get("title") or idea_data.get("startup_name")
            desc = idea_data.get("description") or idea_data.get("idea") or ""
            target_market = (
                idea_data.get("target_market") or idea_data.get("industry")
            )

            combined_prompt = (
                f"{title}: {desc}" if title else desc
            )
            extracted = self.extract_idea(combined_prompt)

        # Merge AI-extracted details with explicit user inputs.
        startup_name = title or extracted.get("startup_name", "Startup Idea")
        industry = target_market or extracted.get("industry", "Unknown")
        problem = extracted.get("problem_statement") or desc
        solution = extracted.get("proposed_solution") or desc
        customers = extracted.get("target_customers") or "Unknown"
        model = extracted.get("business_model") or "Not specified"

        merged = {
            "startup_name": startup_name,
            "industry": industry,
            "problem_statement": problem,
            "proposed_solution": solution,
            "target_customers": customers,
            "business_model": model,
        }

        evaluation = self.evaluate(merged)

        return {
            "title": startup_name,
            "startup_name": startup_name,
            "industry": industry,
            "problem_statement": problem,
            "proposed_solution": solution,
            "target_customers": customers,
            "business_model": model,
            **evaluation,
        }

    async def execute(
        self, idea_data: dict[str, Any] | str
    ) -> dict[str, Any]:
        """Asynchronous execution wrapper."""
        return self.execute_sync(idea_data)

    async def aexecute(
        self, idea_data: dict[str, Any] | str
    ) -> dict[str, Any]:
        """Async alias for execute()."""
        return self.execute_sync(idea_data)


# Singleton instance
idea_agent = IdeaAgent()


if __name__ == "__main__":
    agent = IdeaAgent()
    result = agent.execute_sync(
        "I want to build an AI platform that helps students prepare for interviews."
    )
    print("IdeaAgent Test Result:", result)