# AI-Startup-Idea-Validator - Backend Service

High-performance, modular asynchronous backend powered by **FastAPI**, **Pydantic v2**, and **SQLAlchemy 2.0**. Architected to host an ensemble of autonomous AI agents evaluating startup ideas with live market data.

---

## 📁 Architecture Overview

```
backend/
├── app/
│   ├── api/
│   │   └── routes/             # REST API domain routers (health, idea, search)
│   ├── agents/                 # Multi-agent AI engine (Tavily search, SWOT, reports)
│   ├── core/                   # Global configuration & structured logging
│   ├── models/                 # SQLAlchemy database entities (PostgreSQL)
│   ├── schemas/                # Pydantic v2 request/response contracts
│   ├── services/               # External service adapters (Tavily, LLMs)
│   ├── utils/                  # Sanitizers, parsers, and helper functions
│   └── main.py                 # FastAPI application factory and lifespan hooks
├── tests/                      # Pytest unit and integration suites
├── requirements.txt            # Python dependencies
├── .env.example                # Environment configuration template
└── README.md                   # Developer documentation
```
## 🤖 LLM Integration (Google Gemini)

The backend integrates **Google Gemini** to support AI-powered startup idea analysis and evaluation. The integration is designed to be modular and reusable across AI agents through a centralized LLM service.

### LLM Service

A reusable `LLMService` is implemented in `app/services/llm_service.py` to manage interactions with the Gemini API.

**Features:**
- Google Gemini API integration for AI-powered analysis.
- Synchronous and asynchronous text generation support.
- Structured JSON generation for consistent AI responses.
- JSON parsing and validation support.
- Retry handling for temporary API failures, including service unavailability (503).
- API key and provider configuration through environment variables.
- Heuristic fallback mechanism when external LLM services are unavailable.

### Idea Agent Integration

The `IdeaAgent`, implemented in `app/agents/idea_agent.py`, uses the centralized LLM service to extract startup information and dynamically evaluate startup ideas.

The agent evaluates startup ideas based on the following criteria:

| Evaluation Criteria | Description |
|---|---|
| Problem-Solution Fit | How effectively the proposed solution addresses the identified problem |
| Feasibility | Practicality of implementing the startup idea |
| Uniqueness | Originality and differentiation from existing solutions |
| Problem Clarity | Clarity of the problem and its significance to the target audience |
| Market Potential | Potential demand and business opportunity |
| Solution Defensibility | Potential competitive advantage and long-term sustainability |

### AI-Generated Evaluation Output

The Idea Agent generates structured evaluation results containing:

- Evaluation scores for individual criteria.
- Problem-solution fit analysis.
- Strengths of the proposed startup idea.
- Weaknesses and potential risks.
- Actionable recommendations for improvement.

The evaluation is generated dynamically based on the startup idea rather than relying on fixed evaluation scores.

### Reliability and Fallback Handling

The LLM service incorporates retry logic to handle temporary API failures. When a request encounters a retryable error, the service retries the operation before switching to fallback handling.

If the external LLM service remains unavailable, a local heuristic fallback provides a basic response to ensure the application can continue operating.

Fallback results are intended for preliminary analysis and may not reflect the depth or accuracy of an actual LLM-generated evaluation.

### Testing

The integration was tested through manual execution to verify:

- LLM provider configuration and API key loading.
- Text generation and structured JSON generation workflows.
- Startup idea extraction and evaluation pipeline.
- Retry handling for temporary API failures.
- Fallback behavior when Gemini is unavailable.

During testing, Gemini returned temporary `503 UNAVAILABLE` errors, so the fallback mechanism was exercised. Actual Gemini-generated evaluation could not be confirmed during those test runs.

This integration enables the backend to provide dynamic startup idea evaluations, structured insights, and fallback-based resilience instead of depending solely on predefined evaluation scores.

## 🛠️ Local Development Setup

### 1. Prerequisites
- Python 3.12+
- `pip` package manager

### 2. Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
```
Update `.env` with your API keys (Tavily, LLM) and PostgreSQL credentials when available.

### 4. Run the Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Access Interactive Documentation
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

---

## 🧪 Testing

Execute test suites using `pytest`:
```bash
pytest -v
```

---

## 🚀 Deployment (Render)

The backend is pre-configured for frictionless deployment as a Web Service on **Render**:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**: Configure the secrets specified in `.env.example`.
