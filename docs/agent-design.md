# Multi-Agent System Design Specification

## 1. Overview
The **AI Startup Idea Validator** utilizes an ensemble of specialized, autonomous AI agents. Rather than relying on a single monolithic prompt, each agent is assigned a single responsibility and operates over verified data structures.

---

## 2. Agent Orchestration Architecture

```mermaid
graph TD
    Input[Founder Startup Submission] --> Orchestrator[Coordinator / Orchestrator]
    
    Orchestrator --> SearchAgent[Search Agent<br/>Tavily API]
    SearchAgent --> SearchResults[(Live Market Intelligence)]
    
    SearchResults --> IdeaAgent[Idea Evaluation Agent]
    SearchResults --> MarketAgent[Market Sizing Agent]
    SearchResults --> CompetitorAgent[Competitor Intelligence Agent]
    
    IdeaAgent --> AnalysisOutputs[Aggregated Findings]
    MarketAgent --> AnalysisOutputs
    CompetitorAgent --> AnalysisOutputs
    
    AnalysisOutputs --> SWOTAgent[SWOT Synthesis Agent]
    SWOTAgent --> ReportAgent[Report Synthesis Agent]
    
    ReportAgent --> FinalReport[Structured Validation Dossier & PDF]
```

---

## 3. Agent Responsibilities & Prompt Boundaries

### 3.1 Search Agent (`search_agent.py`)
- **Primary Function**: Discovers real-time market data, existing competitors, and industry trends via the Tavily Search API.
- **Inputs**: Extracted keywords, industry sector, target audience.
- **Outputs**: Deduplicated list of domain articles, competitor URLs, and market summary snippets.

### 3.2 Idea Agent (`idea_agent.py`)
- **Primary Function**: Assesses core problem-solution fit, innovation score, and technical feasibility.
- **Inputs**: User's original idea submission + web context.
- **Outputs**: Feasibility score (0-100), core value proposition summary, key risks.

### 3.3 Market Agent (`market_agent.py`)
- **Primary Function**: Estimates Total Addressable Market (TAM), Serviceable Available Market (SAM), and Serviceable Obtainable Market (SOM), plus regulatory and market trends.
- **Inputs**: Industry classification, geography, target customer segments.
- **Outputs**: Market size figures, CAGR projections, growth drivers.

### 3.4 Competitor Agent (`competitor_agent.py`)
- **Primary Function**: Identifies direct and indirect competitors, competitive moats, and pricing comparisons.
- **Inputs**: Search results, product categories.
- **Outputs**: Competitor profiles (name, strengths, weaknesses, estimated pricing, differentiation vectors).

### 3.5 SWOT Agent (`swot_agent.py`)
- **Primary Function**: Compiles an objective, evidence-based SWOT matrix by synthesizing outputs from the Idea, Market, and Competitor agents.
- **Inputs**: Outputs from IdeaAgent, MarketAgent, and CompetitorAgent.
- **Outputs**: 4-quadrant SWOT breakdown (Strengths, Weaknesses, Opportunities, Threats).

### 3.6 Report Agent (`report_agent.py`)
- **Primary Function**: Formats all structured findings into an executive-ready dossier and prepares it for PDF generation.
- **Inputs**: Consolidated JSON dossier from all agents.
- **Outputs**: Clean Markdown and PDF report artifact.

---

## 4. Execution Strategies (Sequential vs Parallel)
1. **Phase 1 (Data Retrieval)**: `SearchAgent` runs first to establish ground-truth context from live web queries.
2. **Phase 2 (Concurrent Analysis)**: `IdeaAgent`, `MarketAgent`, and `CompetitorAgent` execute concurrently via `asyncio.gather()`.
3. **Phase 3 (Strategic Synthesis)**: `SWOTAgent` processes combined results.
4. **Phase 4 (Packaging)**: `ReportAgent` creates the user-facing report.
