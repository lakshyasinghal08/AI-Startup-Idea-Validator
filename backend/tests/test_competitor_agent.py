"""Tests for the Competitor Intelligence Agent."""

import unittest
from unittest.mock import Mock

from app.agents.competitor_agent import CompetitorAgent


class TestCompetitorAgent(unittest.TestCase):

    def setUp(self):
        self.mock_llm = Mock()
        self.agent = CompetitorAgent(service=self.mock_llm)

        self.idea = {
            "startup_name": "PrepAI",
            "industry": "EdTech",
            "problem_statement": "Students struggle with interview preparation.",
            "proposed_solution": "AI-powered interview preparation platform.",
            "target_customers": "College students and graduates",
            "business_model": "SaaS Subscription",
        }

        self.search_snippets = [
            {
                "title": "InterviewBit Platform",
                "url": "https://example.com/interviewbit",
                "content": "InterviewBit provides technical interview preparation "
                           "and coding practice for students.",
                "score": 0.95,
            },
            {
                "title": "Pramp Interview Practice",
                "url": "https://example.com/pramp",
                "content": "Pramp offers peer-to-peer mock interview practice.",
                "score": 0.90,
            },
        ]

    def test_competitor_analysis_uses_llm(self):
        """Verify competitor analysis uses structured LLM output."""

        expected_result = {
            "direct_competitors": [
                {
                    "name": "InterviewBit",
                    "strengths": ["Coding interview preparation"],
                    "weaknesses": ["Limited evidence available"],
                    "source_urls": ["https://example.com/interviewbit"],
                }
            ],
            "indirect_competitors": [
                {
                    "name": "Pramp",
                    "strengths": ["Peer-to-peer mock interviews"],
                    "weaknesses": ["Limited evidence available"],
                    "source_urls": ["https://example.com/pramp"],
                }
            ],

            "feature_comparison": [
                {
                    "competitor_name": "InterviewBit",
                    "key_features": ["Coding interview preparation"],
                    "target_customers": "Students",
                    "pricing_model": "Not available in sources",
                    "evidence_summary": "Provides technical interview preparation.",
                    "source_urls": ["https://example.com/interviewbit"]
                }
            ],

            "market_gaps": [
                {
                    "gap": "Limited personalized interview feedback",
                    "unmet_customer_need": "Students need personalized feedback.",
                    "opportunity": "Provide AI-powered personalized feedback.",
                    "supporting_evidence": "Potential opportunity requiring further validation.",
                    "source_urls": ["https://example.com/interviewbit"]
                }
            ],

            "comparison_summary": "Both platforms support interview preparation.",
            "competitive_risks": ["Established competitors"],
            "differentiation_opportunities": ["AI-powered personalized feedback"],
            "defensive_moats": ["Proprietary interview performance data"],
        }

        self.mock_llm.generate_structured_json_sync.return_value = expected_result

        result = self.agent.execute(self.idea, self.search_snippets)

        self.assertEqual(result["direct_competitors"], expected_result["direct_competitors"])
        self.assertEqual(result["indirect_competitors"], expected_result["indirect_competitors"])
        self.assertEqual(result["comparison_summary"], expected_result["comparison_summary"])
        self.assertEqual(result["market_gaps"], expected_result["market_gaps"])
        self.assertEqual(result["unique_opportunities"],expected_result["differentiation_opportunities"])
        self.mock_llm.generate_structured_json_sync.assert_called_once()

    def test_llm_receives_startup_and_search_context(self):
        """Verify startup details and search evidence reach the LLM."""

        self.mock_llm.generate_structured_json_sync.return_value = {
            "direct_competitors": [],
            "indirect_competitors": [],
            "comparison_summary": "",
            "competitive_risks": [],
            "differentiation_opportunities": [],
            "defensive_moats": [],
        }

        self.agent.execute(self.idea, self.search_snippets)

        call_args = self.mock_llm.generate_structured_json_sync.call_args

        prompt_text = str(call_args)

        self.assertIn("PrepAI", prompt_text)
        self.assertIn("EdTech", prompt_text)
        self.assertIn("InterviewBit", prompt_text)
        self.assertIn("Pramp", prompt_text)

    def test_invalid_idea_type_raises_type_error(self):
        """Verify passing a non-dict raises TypeError."""
        with self.assertRaises(TypeError):
            self.agent.execute("not a dict")  # type: ignore[arg-type]

    def test_dict_wrapped_search_snippets(self):
        """Verify search_snippets passed as a dict {'search_results': [...]} works correctly."""
        self.mock_llm.generate_structured_json_sync.return_value = {
            "direct_competitors": [],
            "indirect_competitors": [],
            "comparison_summary": "No direct competitors found.",
        }

        wrapped_search = {"search_results": self.search_snippets}
        result = self.agent.execute(self.idea, wrapped_search)
        self.assertIn("direct_competitors", result)


if __name__ == "__main__":
    unittest.main()
