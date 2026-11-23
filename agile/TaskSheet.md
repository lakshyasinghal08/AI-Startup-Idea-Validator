# Agile Task Sheet & Work Allocation Tracking

**Project:** AI-Based Startup Idea Validator with Market Analysis Assistance  
**Program:** Infosys Springboard Virtual Internship 7.0  
**Milestone:** Milestone 1 (Sprint 1)  
**Last Updated:** November 23, 2026  

---

## 1. Master Task Allocation & Delivery Status

| Task ID | Task Description | Owner | Branch | Pull Request | Status | Completion |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **TSK-101** | Repository initialization, Clean Architecture layout, and FastAPI server scaffolding | **Lakshya** | `feature/arch-setup` | PR #1 | **Completed** | 100% |
| **TSK-102** | Centralized Pydantic BaseSettings management, CORS policies, and `.env.example` templates | **Lakshya** | `feature/env-config` | PR #2 | **Completed** | 100% |
| **TSK-103** | LLM Service architecture with Groq LPU primary provider and Google Gemini fallback | **Lakshya** | `feature/llm-service` | PR #3 | **Completed** | 100% |
| **TSK-104** | GitHub Actions CI/CD workflows for automated backend pytest and frontend build verification | **Lakshya** | `feature/ci-cd-pipeline` | PR #4 | **Completed** | 100% |
| **TSK-105** | Overall Milestone 1 technical documentation, architectural synthesis, and pre-submission audit | **Lakshya** | `feature/milestone1-docs` | PR #5 | **Completed** | 100% |
| **TSK-201** | `IdeaAgent` design for structured startup venture attribute extraction from natural language | **Poojitha** | `feature/idea-agent` | PR #6 | **Completed** | 100% |
| **TSK-202** | Pydantic v2 data models for `IdeaCreateRequest`, `IdeaValidationResponse`, and validation schemas | **Poojitha** | `feature/pydantic-schemas` | PR #7 | **Completed** | 100% |
| **TSK-203** | Elimination of synthetic demo data in extraction pipeline; strict HTTP 400 error responses | **Poojitha** | `feature/strict-llm-error` | PR #8 | **Completed** | 100% |
| **TSK-204** | Authoring Business Framework Comparison (`docs/research-note.md`) focusing on Lean Canvas | **Poojitha** | `feature/research-note-biz` | PR #9 | **Completed** | 100% |
| **TSK-301** | `TavilySearchService` REST client integration with response normalization and score validation | **Sahil** | `feature/tavily-service` | PR #10 | **Completed** | 100% |
| **TSK-302** | `SearchAgent` implementation with multi-vector market query generation across 5 research dimensions | **Sahil** | `feature/search-agent` | PR #11 | **Completed** | 100% |
| **TSK-303** | Direct `/api/v1/search/market` API route controller with strict error responses on missing key | **Sahil** | `feature/search-route` | PR #12 | **Completed** | 100% |
| **TSK-304** | Multi-Agent Pattern comparison & Search API evaluation (`docs/research-note.md`) | **Sahil** | `feature/research-note-tech` | PR #13 | **Completed** | 100% |
| **TSK-305** | Backend unit test suite (`test_health.py`) asserting route registration, health probes, and error traps | **Sahil** | `feature/backend-tests` | PR #14 | **Completed** | 100% |
| **TSK-401** | Minimalist UI redesign removing over-engineered animations, complex dashboards, and clutter | **Supritha** | `feature/frontend-clean` | PR #15 | **Completed** | 100% |
| **TSK-402** | Single-input textarea component, dedicated submit trigger, and progressive loading states | **Supritha** | `feature/validator-page` | PR #16 | **Completed** | 100% |
| **TSK-403** | Structured validation report view presenting executive summary, extracted details, and market findings | **Supritha** | `feature/report-view` | PR #17 | **Completed** | 100% |
| **TSK-404** | Centralized Axios HTTP client with interceptors for error banners (`src/api/client.js`) | **Supritha** | `feature/axios-client` | PR #18 | **Completed** | 100% |
| **TSK-405** | Responsive layout optimization, typography polish, and cross-browser accessibility audit | **Supritha** | `feature/ui-responsive` | PR #19 | **Completed** | 100% |

---

## 2. Individual Member Contribution Breakdown

### A. Lakshya Singhal (Project Lead & Architect)
* **Branch Focus:** `feature/arch-setup`, `feature/env-config`, `feature/llm-service`, `feature/ci-cd-pipeline`, `feature/milestone1-docs`
* **Contributions:**
  * Orchestrated the overall decoupled system architecture between FastAPI backend and React frontend.
  * Designed the multi-provider LLM service with failover between Groq Cloud and Google Gemini.
  * Configured GitHub Actions CI workflows for backend pytest runs and frontend Vite builds.
  * Authored system architecture specifications, sprint tracking, and final milestone review documentation.
* **Overall Completion:** 100%

### B. Poojitha B (Senior AI & Backend Engineer)
* **Branch Focus:** `feature/idea-agent`, `feature/pydantic-schemas`, `feature/strict-llm-error`, `feature/research-note-biz`
* **Contributions:**
  * Implemented `IdeaAgent` to parse unstructured natural language startup text into structured venture models.
  * Authored Pydantic v2 validation models (`IdeaCreateRequest`, `ExtractedIdeaModel`, `IdeaValidationResponse`).
  * Hardened extraction routes to return clear HTTP 400 errors (`{"error": "GROQ_API_KEY not configured."}`) when API keys are absent, eliminating synthetic fallback responses.
  * Researched and authored comparative analysis of Lean Canvas, Business Model Canvas, and Value Proposition Canvas.
* **Overall Completion:** 100%

### C. Sahil (Senior Backend & Search Engineer)
* **Branch Focus:** `feature/tavily-service`, `feature/search-agent`, `feature/search-route`, `feature/research-note-tech`, `feature/backend-tests`
* **Contributions:**
  * Built `TavilySearchService` connecting to the live Tavily Search API, with content cleaning and relevance filtering.
  * Designed `SearchAgent` with automated multi-angle query generation covering trends, demand, competitors, pain points, and gaps.
  * Exposed the `/api/v1/search/market` endpoint with strict error handling (`{"error": "TAVILY_API_KEY not configured."}`).
  * Authored unit and integration test suites in `backend/tests/test_health.py` validating 11 test scenarios.
* **Overall Completion:** 100%

### D. Supritha (Senior Frontend & UI/UX Engineer)
* **Branch Focus:** `feature/frontend-clean`, `feature/validator-page`, `feature/report-view`, `feature/axios-client`, `feature/ui-responsive`
* **Contributions:**
  * Simplified and streamlined the frontend into a clean, professional, Notion/ChatGPT-style interface.
  * Built the core Validator interface with ONE textarea, ONE action button, and a progressive multi-step loading spinner.
  * Developed the structured report presentation page displaying executive summary, business model, and live market intelligence.
  * Implemented unified Axios error interception rendering explicit backend error messages in user-friendly banners.
* **Overall Completion:** 100%

---

## 3. Git Workflow & Branching Policy Adherence

All team members strictly followed the agreed Git branching workflow for Milestone 1:
1. Every team member branched off `staging` using standard naming conventions (`feature/<task-name>`).
2. Code was tested locally with unit tests and linting before creating Pull Requests.
3. Pull Requests were submitted against the `staging` branch and reviewed before merging.
4. Per project guidelines, `staging` will not be merged into `main` until mentor review and final approval.
