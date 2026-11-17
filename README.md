# AI-Based Startup Idea Validator with Market Analysis Assistance

<div align="center">

![Infosys Springboard](https://img.shields.io/badge/Infosys_Springboard-Virtual_Internship_7.0-007acc?style=for-the-badge&logo=infosys&logoColor=white)
![Python Version](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React 19](https://img.shields.io/badge/React-19.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<p align="center">
  <strong>An Enterprise-Grade, Multi-Agent AI System for Startup Feasibility Scoring, Real-Time Market Intelligence, Competitor Moat Analysis, and Automated Investment Dossier Synthesis.</strong>
</p>

[Explore Documentation](docs/architecture.md) • [View API Flow](docs/api-flow.md) • [Agent Architecture](docs/agent-design.md) • [Data Models](docs/data-models.md) • [Milestone Report](docs/milestone-1.md)

</div>

---

## 📌 Executive Summary

Early-stage venture creation faces an existential hurdle: **over 90% of startups fail due to lack of market need**. Founders and accelerators spend weeks conducting fragmented manual market sizing, competitive landscape scraping, and subjective SWOT assessments.

The **AI-Based Startup Idea Validator** transforms this process into an automated, data-grounded workflow. Using a **specialized ensemble of autonomous AI agents**, the platform:
- Validates the core problem-solution fit and customer pain points.
- Retrieves live, real-time web intelligence and market signals using the **Tavily Search API**.
- Derives algorithmic **TAM, SAM, and SOM** market sizing calculations.
- Discovers direct and indirect competitors with pricing and moat comparisons.
- Synthesizes an evidence-based, 4-quadrant **Strategic SWOT Matrix**.
- Packages findings into downloadable, investor-ready **Executive Validation Dossiers (PDF & Markdown)**.

---

## 🏛️ System Architecture

The project is structured according to **Clean Architecture** and **Component-Driven Design**, decoupling presentation, business logic, agent orchestration, and persistence layers.

```mermaid
graph TB
    subgraph Client Tier [Presentation Tier - Vercel]
        User([Entrepreneur / Investor]) --> SPA[React 19 Single Page App]
        SPA --> Router[React Router DOM v7]
        Router --> Views[Modular Views: Home | Validator | Reports]
        Views --> AxiosClient[Axios Client with Interceptors]
    end

    subgraph Gateway Tier [API & Security Gateway - Render]
        AxiosClient -->|RESTful JSON / HTTPS| FastAPIGateway[FastAPI ASGI Gateway]
        FastAPIGateway --> CORSSecurity[CORS & Security Policies]
        FastAPIGateway --> RequestLogging[Structured Request Logger]
        FastAPIGateway --> Routers[Versioned Routers: /api/v1/*]
    end

    subgraph Core AI Tier [Autonomous Multi-Agent Network]
        Routers --> Orchestrator[Agent Orchestrator Pipeline]
        Orchestrator --> SearchAgent[1. Search Agent - Tavily Search API]
        SearchAgent -.->|Ground-Truth Context| ContextBus[(Market Context Buffer)]
        
        ContextBus --> IdeaAgent[2. Idea Agent - Feasibility & Value Prop]
        ContextBus --> MarketAgent[3. Market Agent - TAM / SAM / SOM Sizing]
        ContextBus --> CompetitorAgent[4. Competitor Agent - Moat & Landscape]
        
        IdeaAgent & MarketAgent & CompetitorAgent --> SWOTAgent[5. SWOT Agent - Strategic Synthesis]
        SWOTAgent --> ReportAgent[6. Report Agent - PDF / Markdown Brief]
    end

    subgraph Service Tier [External Providers & Foundation Models]
        SearchAgent --> TavilyAPI[Tavily Real-Time Web API]
        IdeaAgent --> LLMService[LLM Engine: OpenAI GPT-4o / Google Gemini]
        MarketAgent --> LLMService
        CompetitorAgent --> LLMService
        SWOTAgent --> LLMService
        ReportAgent --> PDFEngine[ReportLab PDF Engine]
    end

    subgraph Persistence Tier [Data Tier - PostgreSQL]
        Routers --> SQLAlchemyORM[SQLAlchemy 2.0 ORM]
        SQLAlchemyORM --> PostgresDB[(PostgreSQL Relational Database)]
    end
```

---

## 🤖 Multi-Agent Network Specification

| Agent Name | Primary Responsibility | Input Context | Generated Artifact |
| :--- | :--- | :--- | :--- |
| **Search Agent** | Formulates optimal search operators and queries Tavily API for live industry data. | Industry vertical, startup keywords | Verified articles, market snippets, competitor URLs |
| **Idea Agent** | Assesses foundational problem clarity, customer friction, and innovation index. | User submission, web context | Feasibility score (0–100), core value critique |
| **Market Agent** | Analyzes industry CAGR, demographic trends, and computes TAM/SAM/SOM. | Target audience, geographic focus | Quantified market size estimates, growth factors |
| **Competitor Agent** | Identifies existing market leaders, emergent startups, and defensive moats. | Product category, search snippets | Competitor profiles, feature comparison, moats |
| **SWOT Agent** | Cross-correlates multi-agent findings into an objective 4-quadrant strategic matrix. | Outputs of Idea, Market, & Competitor agents | Structured SWOT matrix (S, W, O, T) |
| **Report Agent** | Assembles structured data into executive summaries and compiles PDF dossiers. | Consolidated JSON validation payload | Downloadable PDF dossier & Markdown report |

---

## 💻 Technology Stack

### Frontend Architecture
- **Framework:** [React 19](https://react.dev/) (Component-Based UI Architecture)
- **Tooling & Bundler:** [Vite 6](https://vitejs.dev/) (Blazing fast HMR and optimized production bundles)
- **Styling:** [Tailwind CSS 3.4](https://tailwindcss.com/) (Responsive, utility-first design system)
- **HTTP Client:** [Axios](https://axios-http.com/) (Configured with request/response interceptors)
- **Routing:** [React Router DOM](https://reactrouter.com/) (Declarative client-side routing)
- **Icons:** [Lucide React](https://lucide.dev/) (Consistent modern iconography)

### Backend Architecture
- **Runtime:** [Python 3.12+](https://www.python.org/)
- **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) (High-performance, async ASGI framework)
- **Application Server:** [Uvicorn](https://www.uvicorn.org/) (Lightning-fast ASGI server)
- **Data Validation:** [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings`
- **Database & ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (PostgreSQL-ready declarative models)
- **Environment Management:** `python-dotenv`

### DevOps & Infrastructure
- **Containerization:** Docker & Docker Compose (Multi-service container orchestration)
- **CI/CD:** GitHub Actions (Automated linting, dependency caching, and pytest pipelines)
- **Hosting Targets:**
  - **Frontend:** Vercel (Edge CDN Network)
  - **Backend:** Render (Web Service ASGI Container)
  - **Database:** Render PostgreSQL / Supabase

---

## 📁 Repository Directory Structure

```
AI-Startup-Idea-Validator/
├── .github/
│   └── workflows/
│       ├── backend.yml            # CI: Backend linting, compile, and pytest
│       └── frontend.yml           # CI: Node.js setup, npm dependencies, Vite build
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py    # Router exports
│   │   │   │   ├── health.py      # Health probe (/api/v1/health/)
│   │   │   │   ├── idea.py        # Idea validation endpoints (/api/v1/idea/*)
│   │   │   │   └── search.py      # Market search endpoints (/api/v1/search/*)
│   │   │   └── __init__.py
│   │   │
│   │   ├── agents/                # Autonomous AI Multi-Agent Network
│   │   │   ├── __init__.py
│   │   │   ├── search_agent.py    # Tavily web intelligence agent
│   │   │   ├── idea_agent.py      # Feasibility & value proposition agent
│   │   │   ├── market_agent.py    # TAM / SAM / SOM market sizing agent
│   │   │   ├── competitor_agent.py# Competitive landscape & moat agent
│   │   │   ├── swot_agent.py      # Strategic SWOT matrix agent
│   │   │   └── report_agent.py    # PDF dossier & executive brief agent
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # Centralized Pydantic Settings & CORS
│   │   │   └── logging.py         # Standardized structured application logger
│   │   │
│   │   ├── models/                # SQLAlchemy 2.0 Database Persistence Models
│   │   │   ├── __init__.py        # ORM Base declaration & registry
│   │   │   ├── idea.py            # StartupIdea & ValidationReport models
│   │   │   └── search_result.py   # SearchResultCache model
│   │   │
│   │   ├── schemas/               # Pydantic v2 Request/Response Data Contracts
│   │   │   ├── __init__.py
│   │   │   ├── idea_schema.py     # Request schemas & SWOT definitions
│   │   │   └── response_schema.py # Universal ApiResponse envelope
│   │   │
│   │   ├── services/              # Third-Party API Adapters
│   │   │   ├── __init__.py
│   │   │   ├── tavily_service.py  # Tavily Search API client wrapper
│   │   │   └── llm_service.py     # LLM provider wrapper (OpenAI / Gemini)
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── helpers.py         # Sanitizers, formatting, and ID generators
│   │   │
│   │   └── main.py                # FastAPI application entrypoint & middleware
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_health.py         # Pytest & TestClient validation suite
│   │
│   ├── requirements.txt           # Production Python dependencies
│   ├── .env.example               # Backend environment variables template
│   ├── .gitignore                 # Python virtualenv & bytecode ignore rules
│   ├── Dockerfile                 # ASGI production container specification
│   └── README.md                  # Backend developer guide
│
├── frontend/
│   ├── public/
│   │   └── favicon.svg            # Branded application favicon
│   │
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.js          # Centralized Axios client & interceptors
│   │   │   └── ideaApi.js         # Domain API request methods
│   │   │
│   │   ├── assets/                # Logos and application graphics
│   │   │   └── logo.svg
│   │   │
│   │   ├── components/
│   │   │   └── common/            # Atomic UI primitives
│   │   │       ├── Header.jsx     # Navigation bar with route highlight
│   │   │       ├── Footer.jsx     # Project footer
│   │   │       ├── Button.jsx     # Reusable button with variants
│   │   │       └── Card.jsx       # Standard content container
│   │   │
│   │   ├── context/
│   │   │   └── AppContext.jsx     # Global application state provider
│   │   │
│   │   ├── hooks/
│   │   │   └── useIdeaValidation.js # Custom hook for validation state
│   │   │
│   │   ├── layouts/
│   │   │   └── MainLayout.jsx     # Top-level page layout container
│   │   │
│   │   ├── pages/
│   │   │   ├── HomePage.jsx       # Hero landing page & health probe
│   │   │   ├── ValidatorPage.jsx  # Idea submission form & SWOT viewer
│   │   │   ├── ReportsPage.jsx    # Validation history & PDF download hub
│   │   │   └── NotFoundPage.jsx   # 404 error page
│   │   │
│   │   ├── styles/
│   │   │   └── index.css          # Tailwind CSS directives
│   │   │
│   │   ├── utils/
│   │   │   └── constants.js       # Industry domains, enum values, metadata
│   │   │
│   │   ├── App.jsx                # React Router DOM route hierarchy
│   │   └── main.jsx               # React 19 entrypoint
│   │
│   ├── index.html                 # Single page application HTML shell
│   ├── package.json               # NPM package manifest
│   ├── vite.config.js             # Vite build & reverse-proxy configuration
│   ├── tailwind.config.js         # Tailwind design system configuration
│   ├── postcss.config.js          # PostCSS configuration
│   ├── .gitignore                 # Node & build artifact ignore rules
│   ├── Dockerfile                 # Multi-stage production container build (Nginx)
│   └── README.md                  # Frontend developer guide
│
├── docs/                          # Comprehensive Architectural Documentation
│   ├── architecture.md            # Clean Architecture specification
│   ├── api-flow.md                # REST API schemas & sequence diagrams
│   ├── agent-design.md            # Multi-agent coordination blueprint
│   ├── data-models.md             # Relational ER diagrams & Pydantic contracts
│   └── milestone-1.md             # Milestone 1 delivery report
│
├── docker-compose.yml             # Unified local development orchestration
├── LICENSE                        # Open-source MIT License
├── .gitignore                     # Repository-level ignore rules
└── README.md                      # Master project README
```

---

## ⚡ Quick Start & Local Setup

### Prerequisites
- **Python**: 3.12 or newer
- **Node.js**: v20 or newer (v24 LTS recommended)
- **Docker**: Optional, for containerized local execution

---

### 1. Backend Setup

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a clean virtual environment
# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Initialize environment variables
cp .env.example .env

# 5. Start the FastAPI development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### API Explorer & Documentation:
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Live Health Probe**: [http://127.0.0.1:8000/api/v1/health/](http://127.0.0.1:8000/api/v1/health/)

---

### 2. Frontend Setup

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the Vite development server
npm run dev
```

- **Web Application URL**: [http://localhost:5173](http://localhost:5173)

---

### 3. Containerized Setup (Docker Compose)

To launch the entire stack (FastAPI Backend + React Frontend + PostgreSQL Database) with a single command:

```bash
docker-compose up --build
```

---

## 📡 API Endpoints & Contract Overview

All endpoints return responses encapsulated in a standardized `ApiResponse` envelope:

| Method | Endpoint | Description | Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Root server status and API index | Active |
| `GET` | `/api/v1/health/` | Liveness probe and environment diagnostics | Active |
| `POST` | `/api/v1/idea/validate` | Submits idea for multi-agent evaluation | Milestone 1 (Contract Ready) |
| `GET` | `/api/v1/idea/{idea_id}` | Retrieves validation report by unique ID | Milestone 1 (Contract Ready) |
| `POST` | `/api/v1/search/market` | Runs real-time web search for market insights | Milestone 1 (Contract Ready) |

### Sample Validation Request:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/idea/validate" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "EcoLogix",
       "description": "AI-powered IoT route optimization and cold-chain monitoring for perishable transport.",
       "target_market": "Logistics & Supply Chain",
       "target_audience": "Freight Fleet Managers",
       "estimated_budget": "$50,000",
       "monetization_model": "Monthly B2B SaaS"
     }'
```

### Sample Validation Response:
```json
{
  "success": true,
  "data": {
    "id": "idea_8f4b12a9",
    "title": "EcoLogix",
    "status": "completed",
    "scores": {
      "overall": 82.0,
      "feasibility": 85.0,
      "market_demand": 80.0,
      "uniqueness": 81.0
    },
    "swot": {
      "strengths": ["Strong initial focus on Logistics & Supply Chain", "Clear value proposition defined"],
      "weaknesses": ["High initial customer acquisition costs", "Requires early strategic partnerships"],
      "opportunities": ["Expanding addressable market through AI automation"],
      "threats": ["Rapidly evolving competitive landscape"]
    },
    "summary": "Preliminary validation for 'EcoLogix': Concept demonstrates viable product-market fit indicators.",
    "competitors": ["Competitor One (Market Leader)", "Competitor Two (Emerging Challenger)"],
    "market_sizing": {
      "tam": "$12.8B global sector size",
      "sam": "$2.5B serviceable market",
      "som": "$180M initial beachhead"
    }
  },
  "message": "Idea validation completed successfully",
  "errors": null
}
```

---

## 🌿 Version Control & Git Strategy

Following enterprise Git hygiene:
- **`main`**: **Production branch**. Strictly protected. Contains verified, deployable code. Auto-deploys to production on Vercel and Render.
- **`staging`**: **Integration & Development branch**. Used for active feature testing and staging verification prior to release merges into `main`.
- **Feature Branches**: Formatted as `feature/<milestone-number>-<feature-description>` (e.g. `feature/m2-llm-integration`).

---

## 🎯 Milestone Roadmap

- [x] **Milestone 1: Project Initialization & Clean Architecture**
  - Industry-standard directory skeleton and modular decoupling.
  - FastAPI application with versioned routes (`/api/v1/*`), CORS, and structured logging.
  - React 19 + Vite + Tailwind CSS frontend with component-based architecture.
  - GitHub Actions CI/CD workflows and `docker-compose.yml`.
  - Comprehensive architectural and API documentation (`docs/`).
- [ ] **Milestone 2: LLM Engine & Prompt Engineering**
  - Integration of OpenAI / Google Gemini via `llm_service.py`.
  - Structured prompt chains for problem-solution validation in `idea_agent.py`.
- [ ] **Milestone 3: Real-Time Market Intelligence**
  - Integration of Tavily Search API in `tavily_service.py` and `search_agent.py`.
  - Snippet extraction, noise filtering, and caching layer in `search_result.py`.
- [ ] **Milestone 4: Autonomous Multi-Agent Orchestration**
  - Concurrent execution of `MarketAgent` and `CompetitorAgent`.
  - Synthesis of strategic 4-quadrant matrix via `SWOTAgent`.
- [ ] **Milestone 5: Relational Persistence & User Accounts**
  - PostgreSQL database connectivity with SQLAlchemy 2.0 and Alembic migrations.
  - User authentication and persistent history tracking.
- [ ] **Milestone 6: Analytics Dashboard & Report Generation**
  - Interactive radar and bar charts for validation metrics in React frontend.
  - Investor-ready PDF dossier generation via `ReportLab` in `report_agent.py`.
- [ ] **Milestone 7: Production Deployment & Final Release**
  - Vercel deployment for React 19 frontend.
  - Render deployment for containerized FastAPI backend.
  - End-to-end integration testing and final project submission.

---

## 📚 Documentation Reference

For in-depth architectural and technical blueprints, consult the documentation directory:
- 🏛️ [Clean Architecture Specification](docs/architecture.md)
- 🔄 [API Flow & Sequence Diagrams](docs/api-flow.md)
- 🤖 [Multi-Agent Design Blueprint](docs/agent-design.md)
- 🗄️ [Data Models & Schema Contracts](docs/data-models.md)
- 📋 [Milestone 1 Completion Report](docs/milestone-1.md)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for complete details.

---

<div align="center">
  <sub>Developed for the <strong>Infosys Springboard Virtual Internship 7.0</strong></sub>
</div>
