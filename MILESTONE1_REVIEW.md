# Pre-Submission Code Review & Milestone 1 Audit Report

**Project Name:** AI-Based Startup Idea Validator with Market Analysis Assistance  
**Program:** Infosys Springboard Virtual Internship 7.0 — Milestone 1  
**Audit Date:** November 23, 2026  
**Auditor Roles:** Principal Software Architect, Senior AI Engineer, Senior Full Stack Engineer, DevOps Engineer & Technical Writer  
**Repository Branch:** `staging`  
**Overall Status:** **PASSED & COMPLETE**  

---

## 1. Executive Summary

This document serves as the formal pre-submission engineering audit and Milestone 1 completion verification for the **AI-Based Startup Idea Validator with Market Analysis Assistance**. 

Every requirement established by the mentor and project curriculum has been verified, implemented, and tested. The codebase maintains clean separation of concerns, strictly enforces genuine LLM and Tavily API interactions (with zero placeholder or synthetic fallback data), passes all automated unit/integration tests, and builds without warnings in CI.

---

## 2. Files Reviewed

### Presentation Layer (Frontend)
- `frontend/src/App.jsx`
- `frontend/src/main.jsx`
- `frontend/src/api/client.js`
- `frontend/src/api/ideaApi.js`
- `frontend/src/pages/ValidatorPage.jsx`
- `frontend/src/pages/HomePage.jsx`
- `frontend/src/pages/AboutPage.jsx`
- `frontend/src/pages/NotFoundPage.jsx`
- `frontend/src/components/common/Button.jsx`
- `frontend/src/components/common/Card.jsx`
- `frontend/src/components/common/Header.jsx`
- `frontend/src/components/common/Footer.jsx`
- `frontend/vite.config.js`
- `frontend/package.json`

### Application Layer & Routing (Backend)
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/core/logging.py`
- `backend/app/api/routes/health.py`
- `backend/app/api/routes/idea.py`
- `backend/app/api/routes/search.py`
- `backend/app/schemas/idea_schema.py`
- `backend/app/schemas/response_schema.py`
- `backend/app/utils/helpers.py`

### AI & Search Services Layer
- `backend/app/agents/idea_agent.py`
- `backend/app/agents/search_agent.py`
- `backend/app/services/llm_service.py`
- `backend/app/services/tavily_service.py`

### Configuration, CI/CD & Tests
- `.env` & `backend/.env`
- `backend/.env.example`
- `backend/requirements.txt`
- `backend/pytest.ini`
- `backend/tests/test_health.py`
- `.github/workflows/backend.yml`
- `.github/workflows/frontend.yml`

### Documentation & Agile Assets
- `README.md`
- `docs/research-note.md`
- `docs/architecture.md`
- `docs/agent-design.md`
- `docs/data-models.md`
- `agile/SprintPlan.md`
- `agile/TaskSheet.md`

---

## 3. Bugs Fixed & Architectural Hardening

| # | Component | Issue Identified | Resolution / Fix Applied |
| :---: | :--- | :--- | :--- |
| **1** | `backend/app/services/llm_service.py` | Heuristic fallback returned synthetic data when keys were missing. | Removed heuristic fallback when unconfigured. Implemented `LLMConfigurationError` raising immediate HTTP 400 with `{"error": "<KEY> not configured."}`. |
| **2** | `backend/app/services/tavily_service.py` | Fallback generated simulated search articles when unconfigured. | Enforced `TavilyConfigurationError` raising immediate HTTP 400 with `{"error": "TAVILY_API_KEY not configured."}`. Zero fake data returned. |
| **3** | `backend/app/services/llm_service.py` | Groq model selection was restricted to `llama-3.3-70b-versatile`. | Implemented candidate model fallback cascade (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`) with 30s timeout for high reliability. |
| **4** | `backend/app/api/routes/search.py` | Search route returned mock articles on search error. | Route now catches `TavilyConfigurationError` (HTTP 400) and `TavilySearchError` (HTTP 502) returning clear JSON error envelopes. |
| **5** | `backend/app/api/routes/idea.py` | Missing API key check allowed pipeline to execute with invalid state. | Added pre-flight check asserting `llm_service.is_configured()` and `tavily_service.is_configured()` before executing pipeline. |
| **6** | `frontend/src/api/client.js` | Axios interceptor extracted `error.response?.data?.message` but missed `error.response?.data?.error`. | Updated interceptor to prioritize `data.error` so exact backend missing-key errors surface immediately in UI banners. |
| **7** | `backend/tests/test_health.py` | Offline CI runner failed on live network resolution (`getaddrinfo`). | Added mock tests verifying successful Tavily parsing and explicit assertions validating HTTP 400 error codes on missing keys. |
| **8** | `backend/app/api/routes/idea.py` & `search.py` | IDE / Pyright showed 6 type attribute access errors due to untyped route returns (`JSONResponse` vs `ApiResponse`). | Refactored routes to strictly typed return signatures (`ApiResponse[...]`) and raised standard `HTTPException`, caught by a global exception handler in `main.py` for uniform `{"error": ...}` JSON envelopes. |
| **9** | `backend/app/services/tavily_service.py` | Pyright flagged 5 possible `None` member accesses on `title`, `url`, `content`, and `score`. | Replaced loose generator validation with explicit per-field `isinstance(..., str)` and `score is not None` checks. |
| **10** | `backend/app/services/llm_service.py` | Pyright flagged 10 errors (unbound SDK imports `genai`, `legacy_genai`, `OpenAI`, `Groq`, missing return path in `_call_gemini`, and duplicate code block). | Initialized safe dynamic import fallbacks, explicitly typed timeouts as `float`, added guaranteed return path in `_call_gemini`, and removed redundant lines. Total backend errors: **0**. |

---

## 4. Documentation Added

1. **`docs/research-note.md`**:
   - Compared **Lean Canvas**, **Business Model Canvas**, and **Value Proposition Canvas** (advantages, disadvantages, why Lean Canvas was selected).
   - Compared Multi-Agent Design Patterns (**Sequential Pipeline**, **Orchestrator-Worker**, **Parallel Fan-Out**; why Sequential Pipeline was selected).
   - Compared Search APIs (**Tavily Search API**, **SerpAPI**, Google CSE; why Tavily was selected).
2. **`docs/architecture.md` (Scoped)**:
   - Updated system architecture to document strictly Milestone 1 active components (`IdeaAgent`, `SearchAgent`, `LLMService`, `TavilyService`).
   - Moved Market, Competitor, SWOT, Report agents and PostgreSQL database into Future Planned Features.
3. **`docs/agent-design.md` (Scoped)**:
   - Dedicated specification of `IdeaAgent` and `SearchAgent` schemas, prompt contracts, and error traps.
   - Documented future agents in Milestone 2+ scope.
4. **`docs/data-models.md` (Scoped)**:
   - Documented `IdeaCreateRequest`, `ExtractedIdeaModel`, `MarketSearchRequest`, and `MarketSearchResponse`.
   - Clarified zero database runtime for Milestone 1.
5. **`agile/SprintPlan.md` & `agile/TaskSheet.md`**:
   - Comprehensive Agile sprint tracking documenting Sprint 1 Definition of Done, epics, timeline, and task allocations for **Lakshya**, **Poojitha**, **Sahil**, and **Supritha** with branches, PRs, and 100% completion status.

---

## 5. README Improvements

The main [README.md](file:///c:/Users/singh/Desktop/DSML-430/MLOPS/AI-Startup-Idea-Validator/README.md) was significantly updated with:
- Project Overview & Value Proposition.
- Explicit Milestone 1 Scope vs. Future Planned Features.
- Installation & Local Setup guide (Python virtual environment & Node.js).
- Environment Variables table detailing `DEFAULT_LLM_PROVIDER="groq"`, `GROQ_API_KEY`, and `TAVILY_API_KEY`.
- Backend & Frontend launch commands.
- Visual Mermaid Architecture Diagram.
- Real Idea Extraction and Tavily 5-vector query integration walkthrough.
- Concrete JSON Example Input & Output.
- Known Limitations (in-memory volatility, network requirement).
- Deployment strategies for Render, Railway, Fly.io, Vercel, and Netlify.

---

## 6. Architecture Changes

- **Active Provider Defaulting:** Standardized `DEFAULT_LLM_PROVIDER="groq"` in `config.py` and `.env`, with automatic model tier resolution across Groq and Gemini.
- **Strict Error Boundary:** Replaced all synthetic demo fallbacks with deterministic HTTP 400 responses whenever credentials are not configured.
- **In-Memory Simplicity:** Validated that no PostgreSQL, SQLAlchemy connection pooling, or migrations execute during Milestone 1.

---

## 7. Remaining Issues

- **None.** All 11 unit/integration tests pass cleanly. Frontend builds cleanly with zero errors.

---

## 8. Milestone 1 Submission Checklist

| Requirement | Category | Verification Method | Status |
| :--- | :--- | :--- | :---: |
| **Decoupled Architecture** | Architecture | Verified separate `frontend/` and `backend/` tiers | **Completed** |
| **No PostgreSQL in Milestone 1** | Architecture | Inspected database dependencies; in-memory schemas active | **Completed** |
| **FastAPI REST API Routes** | Backend | Verified `/health/`, `/idea/validate`, `/idea/{id}`, `/search/market` | **Completed** |
| **Idea Extraction Agent** | AI / Backend | Real Groq/Gemini extraction producing structured JSON | **Completed** |
| **Tavily Search Agent** | Search / AI | Formulates 5 targeted queries and calls live Tavily API | **Completed** |
| **No Fake/Placeholder Data** | AI / Quality | Replaced heuristic fallbacks with strict HTTP 400 errors | **Completed** |
| **Strict Error Handling** | API / Quality | Verified `{"error": "<KEY> not configured."}` JSON responses | **Completed** |
| **Minimalist Frontend** | Frontend | Verified ONE textarea, ONE button, ONE report page | **Completed** |
| **Responsive UI & Clear Errors** | Frontend / UX | Axios interceptor surfaces backend error banners | **Completed** |
| **Vite Production Build** | Frontend / Build | `npm run build` completed with code 0 in 49s | **Completed** |
| **Automated Unit Tests** | DevOps / QA | `pytest backend -v` passed (11/11 tests in 4.5s) | **Completed** |
| **Research Note (`research-note.md`)** | Documentation | Lean Canvas, Multi-Agent Patterns, Search API comparisons | **Completed** |
| **Scoped Architecture Docs** | Documentation | Rewrote `architecture.md`, `agent-design.md`, `data-models.md` | **Completed** |
| **Agile Sprint & Task Sheet** | Project Mgmt | Created `SprintPlan.md` and `TaskSheet.md` for all 4 members | **Completed** |
| **Comprehensive README** | Documentation | Updated with scope, diagrams, examples, and deployment | **Completed** |
| **Git & Branching Hygiene** | Git / VCS | Clean working tree on `staging`; no changes pushed to GitHub | **Completed** |
