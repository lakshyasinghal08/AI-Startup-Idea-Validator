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

# Ensure backend root directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.api.routes.health import check_health
from app.api.routes.idea import validate_idea, get_idea_validation
from app.api.routes.search import search_market
from app.schemas.idea_schema import (
    IdeaCreateRequest,
    IdeaValidationResponse,
    MarketSearchRequest,
    MarketSearchResponse,
)


def _extract_paths(fastapi_app):
    """Collect all top-level and mounted router paths from the FastAPI app."""
    paths = {route.path for route in fastapi_app.routes if hasattr(route, "path")}
    paths.update(fastapi_app.openapi().get("paths", {}).keys())
    return list(paths)


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

    def test_idea_validation_controller(self):
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
        self.assertEqual(response.data.title, "CleanRoute AI")
        self.assertEqual(response.data.status, "completed")
        self.assertGreater(response.data.scores.overall, 0.0)
        self.assertGreater(len(response.data.swot.strengths), 0)
        self.assertGreater(len(response.data.swot.weaknesses), 0)
        self.assertGreater(len(response.data.swot.opportunities), 0)
        self.assertGreater(len(response.data.swot.threats), 0)
        self.assertIn("tam", response.data.market_sizing)

    def test_get_idea_validation_by_id(self):
        """Verify GET /api/v1/idea/{idea_id} retrieves validation dossier."""
        test_id = "idea_test_7788"
        response = get_idea_validation(test_id)

        self.assertTrue(response.success)
        self.assertIsInstance(response.data, IdeaValidationResponse)
        self.assertEqual(response.data.id, test_id)
        self.assertIsNotNone(response.data.scores)

    def test_market_search_controller(self):
        """Verify POST /api/v1/search/market executes market query and returns result items."""
        search_payload = MarketSearchRequest(
            query="Autonomous logistics freight optimization",
            max_results=3,
        )
        response = search_market(search_payload)

        self.assertTrue(response.success)
        self.assertIsInstance(response.data, MarketSearchResponse)
        self.assertEqual(response.data.query, "Autonomous logistics freight optimization")
        self.assertGreaterEqual(response.data.total_results, 1)
        self.assertGreaterEqual(len(response.data.results), 1)
        self.assertIsNotNone(response.data.results[0].title)
        self.assertIsNotNone(response.data.results[0].url)

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


def test_pytest_idea_validation():
    """Pytest hook for idea validation endpoint verification."""
    payload = IdeaCreateRequest(
        title="EcoLogix Cargo",
        description="Autonomous IoT cold chain temperature tracking and route optimization.",
        target_market="Logistics & Fleet Operations",
    )
    res = validate_idea(payload)
    assert res.success is True
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