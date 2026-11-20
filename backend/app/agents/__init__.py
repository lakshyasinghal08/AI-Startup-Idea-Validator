"""
Autonomous AI Agents Package
============================
Contains specialized AI agents for multi-agent market validation:
- SearchAgent: Live web research and information gathering.
- IdeaAgent: Problem-solution alignment and value proposition scoring.
- MarketAgent: Market sizing (TAM/SAM/SOM) and growth trajectory analysis.
- CompetitorAgent: Competitive landscape and differentiation mapping.
- SWOTAgent: Structured 4-quadrant SWOT matrix synthesis.
- ReportAgent: Executive report and validation dossier assembly.
"""

from app.agents.search_agent import SearchAgent
from app.agents.idea_agent import IdeaAgent
from app.agents.market_agent import MarketAgent
from app.agents.competitor_agent import CompetitorAgent
from app.agents.swot_agent import SWOTAgent
from app.agents.report_agent import ReportAgent

__all__ = [
    "SearchAgent",
    "IdeaAgent",
    "MarketAgent",
    "CompetitorAgent",
    "SWOTAgent",
    "ReportAgent",
]
