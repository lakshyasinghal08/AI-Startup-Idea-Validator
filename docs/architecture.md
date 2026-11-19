# Architecture Design Specification

## 1. System Overview
The **AI-Based Startup Idea Validator with Market Analysis Assistance** is structured as an enterprise-grade, decoupled client-server application adhering to Clean Architecture principles. It facilitates multi-agent AI research, real-time web querying, and synthesis of startup validation dossiers.

Project Context: **Infosys Springboard Virtual Internship 7.0**

---

## 2. High-Level Architectural Diagram

```mermaid
graph TB
    subgraph ClientTier ["Presentation Layer (React 19 + Vite)"]
        User["End User / Founder"] --> SPA["React 19 Single Page App"]
        SPA --> Router["React Router DOM"]
        Router --> Views["Modular Page Views"]
        Views --> AxiosClient["Axios API Client Layer"]
    end

    subgraph GatewayTier ["API Gateway Layer (FastAPI ASGI)"]
        AxiosClient -->|HTTP / JSON| FastAPIGateway["FastAPI Gateway (:8000)"]
        FastAPIGateway --> CORSMiddleware["CORS Middleware"]
        FastAPIGateway --> RequestLogging["Structured Request Logger"]
        FastAPIGateway --> RouteControllers["Route Controllers (/api/v1)"]
    end

    subgraph ApplicationLogic ["Application & Business Logic"]
        RouteControllers --> HealthRoute["Health API (/health)"]
        RouteControllers --> IdeaRoute["Idea Validation API (/idea)"]
        RouteControllers --> SearchRoute["Search & Discovery API (/search)"]
        
        IdeaRoute --> AgentOrchestrator["Multi-Agent Orchestrator"]
        
        subgraph AgentNetwork ["Autonomous Agent Network"]
            AgentOrchestrator --> SearchAgent["Search Agent"]
            AgentOrchestrator --> IdeaAgent["Idea Validation Agent"]
            AgentOrchestrator --> MarketAgent["Market Analysis Agent"]
            AgentOrchestrator --> CompetitorAgent["Competitor Intelligence Agent"]
            AgentOrchestrator --> SWOTAgent["SWOT Analysis Agent"]
            AgentOrchestrator --> ReportAgent["Report Generation Agent"]
        end
    end

    subgraph ServiceLayer ["Service & Integration Layer"]
        SearchAgent --> TavilyClient["Tavily Search API Client"]
        IdeaAgent --> LLMClient["LLM Client (OpenAI / Gemini)"]
        MarketAgent --> LLMClient
        CompetitorAgent --> LLMClient
        SWOTAgent --> LLMClient
        ReportAgent --> PDFRenderer["Validation Dossier Synthesis Engine"]
    end

    subgraph PersistenceLayer ["Data & Domain Model Layer"]
        M1Store["In-Memory Domain Objects & Mock Data"]
        IdeaRoute -.-> M1Store
    end
```

---

## 3. Layered Design Principles

### 3.1 Presentation Layer (Frontend)
- **Component-Driven Hierarchy**: Isolation of reusable design components (buttons, input fields, cards) from stateful domain containers.
- **Service Layer Abstraction**: UI components never make direct HTTP calls; they invoke dedicated service client functions configured with Axios interceptors (`src/api/client.js`).
- **Client-Side State**: Kept lightweight using React Context for global application state and local component state for forms and view toggles.

### 3.2 Gateway & Routing Layer (FastAPI)
- **Decoupled Routers**: Every domain entity (health, idea, search) is isolated in its own router file under `app/api/routes/`.
- **Validation Pipeline**: Automatic JSON schema parsing, type coercion, and request validation via Pydantic v2.
- **Centralized Lifespan & Config**: Environment configurations managed through `pydantic-settings` with type safety and default fallbacks.

### 3.3 Multi-Agent AI Core
- **Separation of Concerns**: Each agent is responsible for exactly one analysis facet (idea clarity, web search, market sizing, competitor identification, SWOT matrix, and reporting).
- **Prompt Isolation**: System instructions and prompt templates are decoupled from agent execution logic.
- **Deterministic Schemas**: Agents return strictly structured Pydantic models rather than free-form text.

### 3.4 Data Persistence Strategy
- **Lightweight & Standalone**: Pure in-memory domain models and mock data. No running database server or external credentials required. The project starts instantly in any local or cloud environment.

---

## 4. Scalability & Performance Strategy
1. **Asynchronous Execution**: Native async handling across FastAPI routes and external API clients.
2. **Parallel Agent Execution**: Independent agents (such as Market Agent and Competitor Agent) can execute concurrently once web search data is retrieved.
3. **Stateless Backend**: The FastAPI backend contains no server-bound session state, allowing horizontal autoscaling.
4. **Static CDN Caching**: The React 19 application compiles into optimized static assets served globally through Vercel's Edge Network.
