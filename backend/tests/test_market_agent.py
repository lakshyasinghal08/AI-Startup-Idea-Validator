"""
Tests for Market Analysis Agent
===============================
"""

import unittest
from unittest.mock import Mock

from app.agents.market_agent import MarketAgent


class TestMarketAgent(unittest.TestCase):

    def setUp(self):
        self.mock_llm = Mock()
        self.agent = MarketAgent(service=self.mock_llm)

        self.idea = {
            "startup_name": "EcoLogix",
            "industry": "Logistics & Supply Chain",
            "problem": "Freight fleets waste fuel due to static route planning.",
            "solution": "AI dynamic route optimizer reducing carbon emissions.",
            "target_users": "Mid-market fleet managers and dispatchers",
            "business_model": "Monthly SaaS Subscription",
        }

        self.search_snippets = [
            {
                "title": "Global Logistics Market Report 2026",
                "url": "https://example.com/logistics-report",
                "content": "The global fleet management software market is projected to reach $15.5B by 2030, growing at a 13.2% CAGR.",
                "score": 0.94,
            },
            {
                "title": "Freight Optimization Technology Trends",
                "url": "https://example.com/freight-trends",
                "content": "Rising diesel costs and carbon regulations are pushing logistics companies toward automated AI dispatch.",
                "score": 0.89,
            },
        ]

    def test_market_analysis_uses_llm(self):
        """Verify market analysis processes idea and search snippets via LLM."""
        llm_response = {
            "industry": "Logistics & Supply Chain",
            "market_size": "$15.5B Global Fleet Management Market",
            "growth_rate": "13.2% CAGR",
            "customer_segments": ["Mid-market trucking fleets", "Independent freight dispatchers"],
            "target_audience": "Mid-market fleet managers",
            "trends": ["Decarbonization regulations", "Automated dispatch adoption"],
            "demand_indicators": ["Rising diesel costs forcing route efficiency"],
            "opportunities": ["Electric fleet routing integration"],
            "challenges": ["Incumbent telematics vendor lock-in"],
            "tam": "$15.5B Global Market",
            "sam": "$3.2B Mid-market Segment",
            "som": "$220M Realistic 3-Year Beachhead",
            "cagr": "13.2%",
            "market_demand_score": 85.0,
        }
        self.mock_llm.generate_structured_json_sync.return_value = llm_response

        result = self.agent.execute(self.idea, self.search_snippets)

        self.assertEqual(result["industry"], "Logistics & Supply Chain")
        self.assertEqual(result["market_size"], "$15.5B Global Fleet Management Market")
        self.assertEqual(result["growth_rate"], "13.2% CAGR")
        self.assertEqual(len(result["customer_segments"]), 2)
        self.assertEqual(len(result["trends"]), 2)
        self.assertEqual(len(result["opportunities"]), 1)
        self.assertEqual(len(result["challenges"]), 1)
        self.assertIn("tam", result)
        self.assertIn("sam", result)
        self.assertIn("som", result)
        self.assertEqual(result["market_demand_score"], 85.0)
        self.mock_llm.generate_structured_json_sync.assert_called_once()

    def test_llm_receives_idea_and_search_context(self):
        """Verify prompt contains idea attributes and Tavily search text."""
        self.mock_llm.generate_structured_json_sync.return_value = {
            "industry": "Logistics",
            "market_size": "Large",
            "growth_rate": "10%",
            "customer_segments": [],
            "trends": [],
            "opportunities": [],
            "challenges": [],
        }

        self.agent.execute(self.idea, self.search_snippets)

        call_args = str(self.mock_llm.generate_structured_json_sync.call_args)
        self.assertIn("EcoLogix", call_args)
        self.assertIn("Logistics & Supply Chain", call_args)
        self.assertIn("Global Logistics Market Report", call_args)
        self.assertIn("https://example.com/logistics-report", call_args)

    def test_invalid_idea_type_raises_type_error(self):
        """Verify passing a non-dict raises TypeError."""
        with self.assertRaises(TypeError):
            self.agent.execute("raw text instead of dict")  # type: ignore[arg-type]

    def test_dict_wrapped_search_snippets(self):
        """Verify search_snippets passed as a dict {'search_results': [...]} works correctly."""
        self.mock_llm.generate_structured_json_sync.return_value = {
            "industry": "Logistics",
            "market_size": "$10B",
            "growth_rate": "12%",
        }

        wrapped_search = {"search_results": self.search_snippets}
        result = self.agent.execute(self.idea, wrapped_search)
        self.assertIn("industry", result)


if __name__ == "__main__":
    unittest.main()
