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
