
"""
Idea Validation Agent
=====================
Evaluates a startup idea's viability, problem clarity, solution defensibility,
feasibility, uniqueness, and initial product-market fit.
"""

import os
import sys
from typing import Any, Dict

# Ensure backend root directory is in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, "../.."))

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.services.llm_service import LLMService
from app.core.logging import logger


class IdeaAgent:
    """
    Agent responsible for core idea evaluation, feasibility, and scoring.
    """

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()

    async def execute(self, idea_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a startup idea using an LLM and returns structured results.
        """

        title = idea_data.get("title", "Untitled Idea")
        description = idea_data.get("description", "")

        logger.info(f"[IdeaAgent] Evaluating startup idea: {title}")

        system_prompt = """
You are an expert startup analyst and business idea evaluator.

Evaluate startup ideas objectively. Do not blindly praise ideas.
Consider practical business conditions, risks, and market needs.

Return ONLY valid JSON with the following fields:

{
    "overall_score": number,
    "feasibility_score": number,
    "uniqueness_score": number,
    "problem_clarity_score": number,
    "market_potential_score": number,
    "solution_defensibility_score": number,
    "critique": "string",
    "strengths": ["string"],
    "weaknesses": ["string"],
    "recommendations": ["string"]
}

Scoring rules:
- All scores must be between 0 and 100.
- overall_score should represent the overall quality of the startup idea.
- feasibility_score should evaluate whether the idea can realistically be built and launched.
- uniqueness_score should evaluate differentiation from existing solutions.
- problem_clarity_score should evaluate how clearly the idea addresses a real problem.
- market_potential_score should evaluate its potential customer demand and growth.
- solution_defensibility_score should evaluate how difficult it would be for competitors to copy.
- Do not invent research, statistics, or verified market data.
- If information is missing, mention the uncertainty in the critique.
- Keep the critique specific to the submitted startup idea.
"""

        user_prompt = f"""
Evaluate the following startup idea.

Startup Title: {title}

Startup Description: {description}

Additional Information:
{idea_data}

Provide your evaluation in the required JSON format.
"""

        try:
            result = await self.llm_service.generate_structured_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

            logger.info(f"[IdeaAgent] Successfully evaluated idea: {title}")

            return result

        except Exception as e:
            logger.error(f"[IdeaAgent] Evaluation failed for '{title}': {e}")
            raise


if __name__ == "__main__":
    agent = IdeaAgent()
    print("IdeaAgent initialized successfully.")
