"""
Health Endpoint Test Suite
==========================
Verifies that the /api/v1/health endpoint functions correctly.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify the root status endpoint returns 200 OK."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "version" in data


def test_health_check_endpoint():
    """Verify the /api/v1/health endpoint returns healthy status and timestamp."""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "environment" in data


def test_idea_validation_placeholder_endpoint():
    """Verify POST /api/v1/idea/validate accepts payload and returns success envelope."""
    payload = {
        "title": "CleanRoute AI",
        "description": "Green fleet management using AI routing to reduce carbon footprint.",
        "target_market": "Logistics & Fleet Operations",
        "target_audience": "Freight Managers",
        "estimated_budget": "$30,000",
        "monetization_model": "Monthly SaaS",
    }
    response = client.post("/api/v1/idea/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "CleanRoute AI"
    assert "scores" in data["data"]
    assert "swot" in data["data"]


def test_market_search_placeholder_endpoint():
    """Verify POST /api/v1/search/market accepts query and returns results."""
    payload = {
        "query": "AI fleet management solutions",
        "max_results": 3,
    }
    response = client.post("/api/v1/search/market", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["query"] == "AI fleet management solutions"
    assert len(data["data"]["results"]) > 0
