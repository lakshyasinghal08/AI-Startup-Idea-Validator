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

The backend integrates **Google Gemini** to provide AI-powered startup idea evaluation. The integration is designed to be modular, asynchronous, and reusable across AI agents.

### LLM Service

A reusable `LLMService` is implemented in `app/services/llm_service.py` to manage interactions with the Gemini API.

**Features:**
- Google Gemini API integration for AI-powered analysis.
- Asynchronous text generation.
- Structured JSON generation for consistent AI responses.
- JSON parsing and validation support.
- Retry handling for temporary API failures such as service unavailability (503).
- API key management through environment variables.

### Idea Agent Integration

The `IdeaAgent`, implemented in `app/agents/idea_agent.py`, uses the LLM service to evaluate startup ideas and generate structured analysis.

The agent evaluates startup ideas based on the following criteria:

| Evaluation Criteria | Description |
|---|---|
| Overall Score | Overall assessment of the startup idea |
| Feasibility | Practicality of implementing the idea |
| Uniqueness | Originality and differentiation from existing solutions |
| Problem Clarity | Clarity and importance of the problem being addressed |
| Market Potential | Potential demand and business opportunity |
| Solution Defensibility | Competitive advantage and sustainability |

### AI-Generated Evaluation Output

The Idea Agent generates:

- Overall and individual evaluation scores.
- Detailed critique of the startup idea.
- Strengths of the proposed idea.
- Weaknesses and potential risks.
- Actionable recommendations for improvement.

### Reliability

The LLM service includes retry logic for temporary API failures. When a request encounters a temporary error, it retries the operation with increasing delays before reporting failure.

This helps improve reliability when external AI services experience temporary availability issues.

### Testing

The Gemini integration and Idea Agent were manually tested to verify:

- Successful text generation.
- Structured JSON generation and parsing.
- AI-powered startup idea evaluation.
- Retry handling during temporary API failures.

The integration enables the backend to generate dynamic startup evaluations using AI rather than relying on predefined or hardcoded evaluation responses.
---

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
