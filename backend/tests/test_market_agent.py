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
    "market_size": {
        "tam": "Not available in sources",
        "sam": "Not available in sources",
        "som": "Not available in sources",
        "cagr": "15.8% CAGR",
    },
    "market_trends": [
        {
            "trend": "AI tutoring and interview simulator adoption",
            "impact": "Increases demand from students and university career centers.",
            "source_urls": [
                "https://example.com/edtech-market-2026",
                "https://example.com/career-prep",
            ],
        }
    ],
    "demand_drivers": ["Scaling interview coaching for graduates"],
    "target_segments": [
        {
            "segment_name": "Final-Year CS Students",
            "profile": "Undergraduate engineering students preparing for campus placements.",
            "pain_points": ["Lack of personalized mock interview feedback"],
            "willingness_to_pay": "Medium - willing to pay for placement-season subscriptions",
            "priority": "Primary",
        }
    ],
    "market_opportunity_summary": "Strong growth driven by AI adoption in career preparation.",
    "market_risks": ["High competition from free interview prep resources"],
    "source_urls": [
        "https://example.com/edtech-market-2026",
        "https://example.com/career-prep",
    ],
}


def test_market_agent_returns_structured_analysis():
    mock_llm = MagicMock()
    mock_llm.generate_structured_json_sync.return_value = MOCK_LLM_RESPONSE

    agent = MarketAgent(service=mock_llm)
    result = agent.execute(SAMPLE_IDEA, SAMPLE_SNIPPETS)

    assert result["industry"] == "EdTech"
    assert result["market_size"]["cagr"] == "15.8% CAGR"
    assert len(result["market_trends"]) == 1
    assert len(result["target_segments"]) == 1
    assert result["target_segments"][0]["priority"] == "Primary"

    mock_llm.generate_structured_json_sync.assert_called_once()
    call_kwargs = mock_llm.generate_structured_json_sync.call_args.kwargs
    assert "PrepAI" in call_kwargs["user_prompt"]
    assert "https://example.com/edtech-market-2026" in call_kwargs["user_prompt"]


def test_market_agent_handles_empty_search_snippets():
    mock_llm = MagicMock()
    mock_llm.generate_structured_json_sync.return_value = MOCK_LLM_RESPONSE

    agent = MarketAgent(service=mock_llm)
    result = agent.execute(SAMPLE_IDEA, [])

    assert isinstance(result, dict)
    mock_llm.generate_structured_json_sync.assert_called_once()


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

    with pytest.raises(ValueError, match="extracted_idea must be a non-empty dictionary"):
        agent.execute({}, SAMPLE_SNIPPETS)


def test_market_agent_raises_on_invalid_llm_response():
    mock_llm = MagicMock()
    mock_llm.generate_structured_json_sync.return_value = None

    agent = MarketAgent(service=mock_llm)

    with pytest.raises(ValueError, match="invalid response"):
        agent.execute(SAMPLE_IDEA, SAMPLE_SNIPPETS)


def test_market_agent_raises_on_missing_required_keys():
    mock_llm = MagicMock()
    mock_llm.generate_structured_json_sync.return_value = {
        "industry": "EdTech",
        "market_size": {"cagr": "15.8% CAGR"},
    }

    agent = MarketAgent(service=mock_llm)

    with pytest.raises(ValueError, match="missing required keys"):
        agent.execute(SAMPLE_IDEA, SAMPLE_SNIPPETS)


def test_market_agent_propagates_llm_service_error():
    mock_llm = MagicMock()
    mock_llm.generate_structured_json_sync.side_effect = RuntimeError("API key missing")

    agent = MarketAgent(service=mock_llm)

    with pytest.raises(RuntimeError, match="API key missing"):
        agent.execute(SAMPLE_IDEA, SAMPLE_SNIPPETS)