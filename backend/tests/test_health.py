"""
Health & API Route Test Suite
=============================
Purpose:
    Validates core FastAPI routes (/health, /idea/validate, /idea/{id}, /search/market, /).
    Architected for high portability:
- Runs cleanly under pytest in CI/CD pipeline.
- Runs cleanly under direct Python execution.

Infosys Springboard Virtual Internship 7.0 - Milestone 1
"""

import os
import sys
import unittest
from unittest.mock import patch

# Ensure backend root directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.api.routes.health import check_health
from app.api.routes.idea import get_idea_validation, validate_idea
from app.api.routes.search import search_market
from app.main import app
from app.schemas.idea_schema import (
    IdeaCreateRequest,
    IdeaValidationResponse,
    MarketSearchRequest,
    MarketSearchResponse,
)
from fastapi import HTTPException


def _extract_paths(fastapi_app):
    """Collect all top-level and mounted router paths from the FastAPI app."""
    paths = {route.path for route in fastapi_app.routes if hasattr(route, "path")}
    paths.update(fastapi_app.openapi().get("paths", {}).keys())
    return list(paths)


MOCK_EXTRACTED_IDEA = {
    "startup_name": "CleanRoute AI",
    "industry": "Logistics & Fleet Operations",
    "problem_statement": "Green fleet management using AI routing to reduce carbon footprint for freight.",
    "proposed_solution": "Autonomous IoT cold chain temperature tracking and route optimization.",
    "target_customers": "Freight Dispatchers",
    "business_model": "Monthly SaaS Subscription",
    "value_proposition": "Automated route optimization reducing fuel usage by 20%.",
}

MOCK_SEARCH_RESULTS = [
    {
        "title": "CleanRoute Overview",
        "url": "https://example.com/cleanroute",
        "content": "CleanRoute provides automated freight route optimization.",
        "score": 0.92,
    }
]

MOCK_MARKET_DATA = {
    "industry": "Logistics & Fleet Operations",
    "market_size": "$14.2B Global Logistics Software",
    "growth_rate": "12.4% CAGR",
    "customer_segments": ["Mid-market Fleet Operators", "Freight Dispatchers"],
    "trends": ["Autonomous routing adoption", "Decarbonization tracking"],
    "opportunities": ["Real-time emissions reporting"],
    "challenges": ["Incumbent telematics integration"],
    "tam": "$14.2B Global Market",
    "sam": "$2.8B Mid-market Segment",
    "som": "$210M 3-Year Beachhead",
    "cagr": "12.4%",
    "demand_drivers": "High diesel costs and green fleet mandates",
    "market_demand_score": 84.0,
}

MOCK_COMPETITOR_DATA = {
    "direct_competitors": [
        {
            "name": "Route4Me",
            "strengths": ["Established routing network"],
            "weaknesses": ["Legacy user interface"],
            "features": ["Dynamic dispatch"],
            "pricing": "$149/mo",
            "source_urls": ["https://example.com/route4me"],
        }
    ],
    "indirect_competitors": [],
    "strengths": ["AI-driven carbon optimization"],
    "weaknesses": ["Early-stage brand"],
    "market_gaps": ["Affordable emissions reduction for freight"],
    "risks": ["Established telematics players adding routing"],
    "unique_opportunities": ["Proprietary green routing models"],
    "comparison_summary": "CleanRoute provides specialized carbon-optimized routing.",
}


class TestHealthAndRoutes(unittest.TestCase):
    """
    Test cases verifying API contracts, response models, and status envelopes.
    """

    def test_health_check_controller(self):
        """Verify the health check controller returns healthy status and metadata."""
        result = check_health()
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("status"), "healthy")
        self.assertIn("app_name", result)
        self.assertIn("environment", result)
        self.assertIn("version", result)
        self.assertIn("timestamp", result)

    @patch("app.api.routes.idea.competitor_agent.execute", return_value=MOCK_COMPETITOR_DATA)
    @patch("app.api.routes.idea.market_agent.execute", return_value=MOCK_MARKET_DATA)
    @patch("app.api.routes.idea.llm_service.is_configured", return_value=True)
    @patch("app.api.routes.idea.idea_agent.extract_idea", return_value=MOCK_EXTRACTED_IDEA)
    @patch("app.api.routes.idea.search_agent.execute", return_value=MOCK_SEARCH_RESULTS)
    def test_idea_validation_controller(self, mock_search, mock_extract, mock_config, mock_market, mock_comp):
        """Verify POST /api/v1/idea/validate processes valid payload and returns structured SWOT."""
        request_payload = IdeaCreateRequest(
            title="CleanRoute AI",
            description="Green fleet management using AI routing to reduce carbon footprint for freight.",
            target_market="Logistics & Fleet Operations",
            target_audience="Freight Dispatchers",
            estimated_budget="$35,000",
            monetization_model="Monthly SaaS Subscription",
        )
        response = validate_idea(request_payload)

        self.assertTrue(response.success)
        self.assertIsInstance(response.data, IdeaValidationResponse)
        assert response.data is not None
        self.assertEqual(response.data.title, "CleanRoute AI")
        self.assertEqual(response.data.status, "completed")
        self.assertGreater(response.data.scores.overall, 0.0)
        self.assertGreater(len(response.data.swot.strengths), 0)
        self.assertGreater(len(response.data.swot.weaknesses), 0)
        self.assertGreater(len(response.data.swot.opportunities), 0)
        self.assertGreater(len(response.data.swot.threats), 0)
        self.assertIn("tam", response.data.market_sizing)

    @patch("app.api.routes.idea.competitor_agent.execute", return_value=MOCK_COMPETITOR_DATA)
    @patch("app.api.routes.idea.market_agent.execute", return_value=MOCK_MARKET_DATA)
    @patch("app.api.routes.idea.idea_agent.extract_idea", return_value=MOCK_EXTRACTED_IDEA)
    @patch("app.api.routes.idea.search_agent.execute", return_value=MOCK_SEARCH_RESULTS)
    @patch("app.api.routes.idea.llm_service.is_configured", return_value=True)
    def test_single_input_idea_validation(self, mock_config, mock_search, mock_extract, mock_market, mock_comp):
        """Verify POST /api/v1/idea/validate processes single raw text input."""
        payload = IdeaCreateRequest(
            idea="I want to build an AI platform that helps students prepare for interviews."
        )
        response = validate_idea(payload)

        self.assertTrue(response.success)
        self.assertIsInstance(response.data, IdeaValidationResponse)
        assert response.data is not None
        self.assertEqual(response.data.status, "completed")
        self.assertGreater(response.data.overall_validation_score, 0.0)
        self.assertIsNotNone(response.data.executive_summary)
        self.assertIsNotNone(response.data.market_research)
        self.assertIsNotNone(response.data.executive_summary)
        self.assertIsNotNone(response.data.market_research)

    def test_get_idea_validation_by_id(self):
        """Verify GET /api/v1/idea/{idea_id} retrieves validation dossier."""
        test_id = "idea_test_7788"
        response = get_idea_validation(test_id)

        self.assertTrue(response.success)
        self.assertIsInstance(response.data, IdeaValidationResponse)
        assert response.data is not None
        self.assertEqual(response.data.id, test_id)
        self.assertIsNotNone(response.data.scores)

    @patch("app.api.routes.search.tavily_service.search")
    def test_market_search_controller(self, mock_search):
        """Verify POST /api/v1/search/market executes market query and returns result items."""
        mock_search.return_value = [
            {
                "title": "Autonomous logistics overview",
                "url": "https://example.com/logistics",
                "content": "Autonomous freight optimization is expanding rapidly.",
                "score": 0.95,
            }
        ]
        search_payload = MarketSearchRequest(
            query="Autonomous logistics freight optimization",
            max_results=3,
        )
        response = search_market(search_payload)

        self.assertTrue(response.success)
        self.assertIsInstance(response.data, MarketSearchResponse)
        assert response.data is not None
        self.assertEqual(response.data.query, "Autonomous logistics freight optimization")
        self.assertGreaterEqual(response.data.total_results, 1)
        self.assertGreaterEqual(len(response.data.results), 1)
        self.assertEqual(response.data.results[0].title, "Autonomous logistics overview")
        self.assertEqual(response.data.results[0].url, "https://example.com/logistics")

    def test_market_search_missing_key_error(self):
        """Verify POST /api/v1/search/market raises 400 error when TAVILY_API_KEY is not configured."""
        with patch("app.api.routes.search.tavily_service.is_configured", return_value=False):
            search_payload = MarketSearchRequest(query="AI startups")
            with self.assertRaises(HTTPException) as ctx:
                search_market(search_payload)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("TAVILY_API_KEY not configured", str(ctx.exception.detail))

    def test_idea_validate_missing_key_error(self):
        """Verify POST /api/v1/idea/validate raises 400 error when LLM API key is not configured."""
        with patch("app.api.routes.idea.llm_service.is_configured", return_value=False):
            payload = IdeaCreateRequest(idea="Test idea")
            with self.assertRaises(HTTPException) as ctx:
                validate_idea(payload)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("not configured", str(ctx.exception.detail))

    def test_app_routes_registration(self):
        """Verify all required API endpoints are mounted on the FastAPI application."""
        registered_paths = _extract_paths(app)
        expected_paths = [
            "/",
            "/api/v1/health/",
            "/api/v1/idea/validate",
            "/api/v1/idea/{idea_id}",
            "/api/v1/search/market",
            "/docs",
            "/openapi.json",
        ]
        for path in expected_paths:
            self.assertIn(
                path,
                registered_paths,
                f"Expected route '{path}' was not found in registered app routes: {registered_paths}",
            )


# Pytest-compatible standalone function assertions
def test_pytest_health():
    """Pytest hook for health check verification."""
    data = check_health()
    assert data["status"] == "healthy"
    assert "version" in data

@patch("app.api.routes.idea.competitor_agent.execute", return_value=MOCK_COMPETITOR_DATA)
@patch("app.api.routes.idea.market_agent.execute", return_value=MOCK_MARKET_DATA)
@patch("app.api.routes.idea.idea_agent.extract_idea", return_value=MOCK_EXTRACTED_IDEA)
@patch("app.api.routes.idea.search_agent.execute", return_value=MOCK_SEARCH_RESULTS)
@patch("app.api.routes.idea.llm_service.is_configured", return_value=True)
def test_pytest_idea_validation(mock_config, mock_search, mock_extract, mock_market, mock_comp):
    """Pytest hook for idea validation endpoint verification."""
    payload = IdeaCreateRequest(
        title="EcoLogix Cargo",
        description="Autonomous IoT cold chain temperature tracking and route optimization.",
        target_market="Logistics & Fleet Operations",
    )
    res = validate_idea(payload)
    assert res.success is True
    assert res.data is not None
    assert res.data.title == "EcoLogix Cargo"
    assert res.data.status == "completed"


def test_pytest_routes():
    """Pytest hook for route registration verification."""
    paths = _extract_paths(app)
    assert "/api/v1/health/" in paths
    assert "/api/v1/idea/validate" in paths
    assert "/api/v1/search/market" in paths


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHealthAndRoutes)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
