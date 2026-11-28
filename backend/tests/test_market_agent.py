"""
Unit tests for MarketAgent (Market Opportunity & Customer Segmentation).
"""

from unittest.mock import MagicMock
import pytest

from app.agents.market_agent import MarketAgent


SAMPLE_IDEA = {
    "startup_name": "PrepAI",
    "industry": "EdTech",
    "problem_statement": "Students struggle with technical interview preparation.",
    "proposed_solution": "AI-powered mock interview and feedback platform.",
    "target_customers": "College students and recent graduates",
}

SAMPLE_SNIPPETS = [
    {
        "title": "Global EdTech Market Report 2026",
        "url": "https://example.com/edtech-market-2026",
        "content": "The global EdTech market is projected to grow at 15.8% CAGR driven by AI tutoring.",
        "score": 0.91,
    },
    {
        "title": "Career Prep Trends",
        "url": "https://example.com/career-prep",
        "content": "University career centers are adopting AI interview simulators to scale coaching.",
        "score": 0.84,
    },
]

MOCK_LLM_RESPONSE = {
    "industry": "EdTech",
    "market_size": "$8.5B Global EdTech Market",
    "growth_rate": "15.8% CAGR",
    "customer_segments": ["Final-Year CS Students", "University Career Centers"],
    "trends": ["AI tutoring and interview simulator adoption"],
    "opportunities": ["Scaling mock interview coaching for graduates"],
    "challenges": ["Competition from free interview prep platforms"],
    "demand_indicators": ["Rising campus placement prep spending"],
    "tam": "$8.5B",
    "sam": "$1.9B",
    "som": "$140M",
    "cagr": "15.8% CAGR",
    "market_demand_score": 85.0,
}


def test_market_agent_returns_standardized_analysis():
    mock_llm = MagicMock()
    mock_llm.generate_structured_json_sync.return_value = MOCK_LLM_RESPONSE

    agent = MarketAgent(service=mock_llm)
    result = agent.execute(SAMPLE_IDEA, SAMPLE_SNIPPETS)

    assert result["industry"] == "EdTech"
    assert result["cagr"] == "15.8% CAGR"
    assert len(result["trends"]) == 1
    assert len(result["customer_segments"]) == 2
    assert "https://example.com/edtech-market-2026" in result["source_urls"]
    assert result["market_demand_score"] == 85.0

    mock_llm.generate_structured_json_sync.assert_called_once()
    call_kwargs = mock_llm.generate_structured_json_sync.call_args.kwargs
    assert "PrepAI" in call_kwargs["user_prompt"]
    assert "https://example.com/edtech-market-2026" in call_kwargs["user_prompt"]


def test_market_agent_accepts_dict_wrapped_search_results():
    mock_llm = MagicMock()
    mock_llm.generate_structured_json_sync.return_value = MOCK_LLM_RESPONSE

    agent = MarketAgent(service=mock_llm)
    result = agent.execute(SAMPLE_IDEA, {"search_results": SAMPLE_SNIPPETS})

    assert isinstance(result, dict)
    assert "https://example.com/edtech-market-2026" in result["source_urls"]


def test_market_agent_filters_malformed_snippets():
    mock_llm = MagicMock()
    mock_llm.generate_structured_json_sync.return_value = MOCK_LLM_RESPONSE

    bad_snippets = [
        "not-a-dict",
        {"title": "Missing URL", "content": "Some text"},
        {"title": "Valid", "url": "https://example.com/valid", "content": "Valid content"},
    ]

    agent = MarketAgent(service=mock_llm)
    agent.execute(SAMPLE_IDEA, bad_snippets)

    user_prompt = mock_llm.generate_structured_json_sync.call_args.kwargs["user_prompt"]
    assert "https://example.com/valid" in user_prompt
    assert "Missing URL" not in user_prompt


def test_market_agent_raises_on_invalid_idea_input():
    mock_llm = MagicMock()
    agent = MarketAgent(service=mock_llm)

    with pytest.raises(TypeError, match="dictionary"):
        agent.execute("not-a-dict", SAMPLE_SNIPPETS)

    with pytest.raises(ValueError, match="non-empty dictionary"):
        agent.execute({}, SAMPLE_SNIPPETS)


def test_market_agent_raises_on_invalid_llm_response():
    mock_llm = MagicMock()
    mock_llm.generate_structured_json_sync.return_value = None

    agent = MarketAgent(service=mock_llm)

    with pytest.raises(TypeError, match="invalid response"):
        agent.execute(SAMPLE_IDEA, SAMPLE_SNIPPETS)


def test_market_agent_raises_on_missing_required_fields():
    mock_llm = MagicMock()
    mock_llm.generate_structured_json_sync.return_value = {"industry": "EdTech"}

    agent = MarketAgent(service=mock_llm)

    with pytest.raises(ValueError, match="missing required"):
        agent.execute(SAMPLE_IDEA, SAMPLE_SNIPPETS)


def test_market_agent_propagates_llm_service_error():
    mock_llm = MagicMock()
    mock_llm.generate_structured_json_sync.side_effect = RuntimeError("API key missing")

    agent = MarketAgent(service=mock_llm)

    with pytest.raises(RuntimeError, match="API key missing"):
        agent.execute(SAMPLE_IDEA, SAMPLE_SNIPPETS)