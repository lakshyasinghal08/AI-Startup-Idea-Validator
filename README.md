# AI-Based Startup Idea Validator with Market Analysis Assistance

<div align="center">

![Infosys Springboard](https://img.shields.io/badge/Infosys_Springboard-Virtual_Internship_7.0-007acc?style=for-the-badge&logo=infosys&logoColor=white)
![Author](https://img.shields.io/badge/Author-Lakshya_Singhal-blue?style=for-the-badge&logo=github)
![Python Version](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React 19](https://img.shields.io/badge/React-19.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<p align="center">
  <strong>An Enterprise-Grade, Multi-Agent AI System for Startup Feasibility Scoring, Real-Time Market Intelligence, Competitor Moat Analysis, and Automated Investment Dossier Synthesis.</strong>
</p>

[Explore Documentation](docs/architecture.md) • [View API Flow](docs/api-flow.md) • [Agent Architecture](docs/agent-design.md) • [Data Models](docs/data-models.md) • [Milestone Report](docs/milestone-1.md)

</div>

---

## 📌 Executive Summary

Early-stage venture creation faces an existential hurdle: **over 90% of startups fail due to lack of market need**. Founders, accelerators, and venture evaluators spend weeks conducting fragmented manual market sizing, competitive landscape scraping, and subjective SWOT assessments.

The **AI-Based Startup Idea Validator** transforms this process into an automated, data-grounded workflow. Using a **specialized ensemble of autonomous AI agents**, the platform:
- **Single-Input Natural Language Interface:** Accepts a single startup description (e.g., *"I want to build an AI platform that helps students prepare for interviews."*) and automatically extracts core dimensions (problem, solution, audience, industry, model) via LLM.
- **Multi-Provider LLM Integration:** Powered by Google Gemini (Priority 1), OpenAI (Priority 2), and Groq (Priority 3) with intelligent fallback resilience.
- **Live Market Web Intelligence:** Retrieves live industry trends, competitive signals, and market demand using the **Tavily Search API**.
- **Market Sizing Projections:** Derives algorithmic **TAM, SAM, SOM**, and **CAGR** growth metrics tailored to the vertical.
- **Competitive Moat Analysis:** Maps direct incumbents, indirect substitutes, and sustainable defensive moats.
- **Strategic SWOT Matrix:** Synthesizes internal strengths and external threats into an objective 4-quadrant strategic matrix.
- **13-Section Consulting Dossier:** Formatted in top-tier management consulting style (McKinsey, BCG, Deloitte) with cards, clean typography, validation scoring, and zero chart clutter.

> **Note on Architecture & Deployment:** The project is deliberately designed to be **lightweight, modular, and self-contained**. It runs directly on your local machine using standard Python and Node.js in-memory without requiring Docker or any external database setup, making it immediately testable and reproducible for evaluations. Database persistence is planned for Milestone 5.

---

## 🏛️ System Architecture

The project is structured according to **Clean Architecture** and **Component-Driven Design**, decoupling presentation, API validation, agent orchestration, external integrations, and in-memory domain models.

```mermaid
flowchart TD
    subgraph ClientTier ["Presentation Layer (React 19 + Vite)"]
        User["Entrepreneur / Investor"] --> SPA["React 19 Single Page App"]
        SPA --> Router["React Router DOM v7"]
        Router --> Views["Pages: Home, Validator (13-Section Report), About"]
        Views --> AxiosClient["Axios HTTP Client (client.js / ideaApi.js)"]
    end

    AxiosClient -- "RESTful JSON Request" --> FastAPIGateway

    subgraph GatewayTier ["API Gateway Layer (FastAPI ASGI :8000)"]
        FastAPIGateway["FastAPI Application (main.py)"]
        FastAPIGateway --> CORSSecurity["CORS & Origin Security (config.py)"]
        FastAPIGateway --> RequestLogging["Structured Request Logger (logging.py)"]
        FastAPIGateway --> Schemas["Pydantic v2 Schemas (idea_schema / response_schema)"]
        Schemas --> Routers["Versioned API Routers (/api/v1/health, /idea, /search)"]
    end

    Routers --> Orchestrator
    Routers <--> DomainModels

    subgraph CoreAITier ["Autonomous Multi-Agent Network (backend/app/agents)"]
        Orchestrator["Multi-Agent Orchestrator Pipeline"]
        Orchestrator --> SearchAgent["1. Search Agent (search_agent.py)"]
        SearchAgent -. "Market Context" .-> ContextBus["Market Intelligence Buffer"]

        ContextBus --> IdeaAgent["2. Idea Agent (Feasibility & Value Prop)"]
        ContextBus --> MarketAgent["3. Market Agent (TAM / SAM / SOM Sizing)"]
        ContextBus --> CompetitorAgent["4. Competitor Agent (Moats & Landscape)"]

        IdeaAgent & MarketAgent & CompetitorAgent --> SWOTAgent["5. SWOT Agent (Strategic Synthesis)"]
        SWOTAgent --> ReportAgent["6. Report Agent (Validation Dossier)"]
    end

    subgraph PersistenceTier ["Data & Domain Model Layer (In-Memory)"]
        DomainModels["Domain Entity Models (StartupIdea, ValidationReport)"]
        DomainModels --> CacheStore["SearchResultCache (search_result.py)"]
    end

    subgraph ServiceTier ["External Services & Foundation Models (backend/app/services)"]
        TavilyAPI["Tavily Real-Time Web Search (tavily_service.py)"]
        LLMService["LLM Provider: Gemini / OpenAI / Groq (llm_service.py)"]
    end

    SearchAgent <--> TavilyAPI
    IdeaAgent & MarketAgent & CompetitorAgent & SWOTAgent & ReportAgent <--> LLMService
    ReportAgent -- "Structured ApiResponse JSON" --> Routers
    Routers -- "Validation Report JSON" --> AxiosClient