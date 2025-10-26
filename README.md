# Mobile Shopping Agent (Google ADK)

An end-to-end Gemini-powered shopping assistant built with the Google Agent Development Kit (ADK). The agent ingests a curated catalogue of mobile phones, answers natural-language queries, compares devices, and renders recommendations in a responsive React chat UI.

## Live Demo
- Frontend (Vercel): https://mobile-shopping-agent-frontend-nitin23329s-projects.vercel.app?_vercel_share=AI7h6MowlQKC9mhHUfshpdfKNpmBaZPf
- Backend API (Hugging Face Spaces): https://nitin23329-mobile-shopping-agent-backend.hf.space/ (Swagger docs at https://nitin23329-mobile-shopping-agent-backend.hf.space/docs)

## Local Development

### Prerequisites
- Python 3.11 with Conda (recommended).
- Node.js 18 LTS (via `nvm` or system installer).
- Supabase project and service role key + Google AI Studio key + RapidAPI credentials for data refreshes.

### Clone the repo
```bash
git clone https://github.com/NITIN23329/mobile-shopping-agent.git
cd mobile-shopping-agent
```

### Backend setup
```bash
conda create -n mobile-shopping-agent python=3.11
conda activate mobile-shopping-agent
pip install -r requirements.txt
```

Create `.env` in the project root:
```
GOOGLE_API_KEY=your_google_ai_studio_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=mobile-phones2.p.rapidapi.com
API_REQUEST_TIMEOUT_SECONDS=120
```

Run locally:
```bash
uvicorn backend.api:app --reload --port 8000
# health check: curl http://localhost:8000/health
```

### Frontend setup
```bash
cd frontend
npm install
```

Populate `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

Run the dev server:
```bash
npm run dev
```

### Run frontend and backend together
- Terminal A: `conda activate mobile-shopping-agent && uvicorn backend.api:app --reload --port 8000`
- Terminal B: `cd frontend && npm run dev`

Visit http://127.0.0.1:3000/ to chat with the agent. Structured phone cards render beneath each agent reply.


## Feature Highlights
- Conversational search that extracts intent (budget, brand, key features) from free-form prompts.
- Comparison mode that contrasts two to three phones with structured spec cards and trade-off summaries.
- Explainable recommendations reasoned directly from Supabase-sourced catalogue facts.
- Safety guardrails that deflect adversarial prompts (prompt leakage, API key requests, toxic brand bashing).
- Mobile-first web interface with product cards, comparison table, and persistent session management.

## Architecture & Tech Stack

### Frontend (Vercel)
- React 18 + Vite + TypeScript front-end served as static assets on Vercel.
- Tailwind CSS handles adaptive layout; custom hooks (`useChat`) coordinate API calls, optimistic UI, and timeout handling.
- Axios/fetch abstraction in `frontend/src/api` attaches session identifiers and feeds responses into the card/comparison renderer.

### Backend (Hugging Face Spaces)
- FastAPI app (`backend/api.py`) exposes `/chat` and `/health` endpoints behind Uvicorn, packaged via Docker for Spaces.
- Google Agent Development Kit bootstraps Gemini models through LiteLLM, enabling tool orchestration and streaming responses.
- Dependency layer uses Pydantic models for request/response validation and structured traces.

### Google ADK Agent Orchestration
- Primary agent defined in `backend/agent.py` runs a planner-executor loop that evaluates user intent and invokes tools.
- Tool set (`backend/tools.py`) contains:
  - `search_catalogue` querying Supabase Postgres via RPC for budget/feature filters.
  - `compare_models` assembling diff views and spec highlights for up to three handsets.
  - `explain_feature` returning glossary-style summaries (e.g., OIS vs EIS) grounded in curated content.
- Routing logic leans on ADK conversation memory to preserve context, with guardrails injected from `agent_instructions.py`.

### Data & Persistence
- RapidAPI `apikite/mobile-phones2` feed ingested through `backend/supabase_upload/data_upload.py`, normalized, and stored in Supabase tables.
- Supabase service role key grants read/write access; runtime queries use row-level security safe service role channel restricted to deployed backend.
- Postgres schema maintains device metadata, spec groups, and price bands to support structured comparisons.

### Configuration & Tooling
- Environment variables managed through `.env` locally and platform secret stores in production (Vercel + Spaces).
- Conda environment isolates Python dependencies; Node.js ≥18 (via `nvm`) supports Vite build tooling.
- Logging hooks prepared for integration with Hugging Face Space logs and Vercel analytics; optional DEBUG flag surfaces developer diagnostics.

### End-to-end Request Flow
1. User submits a query through the Vercel frontend; `useChat` stamps a session ID and dispatches to `/chat`.
2. FastAPI validates payloads, spins up a Google ADK `AgentSession`, and feeds the message into Gemini with system instructions.
3. Gemini planner calls custom tools as needed (search, compare, explain); each tool in turn queries Supabase or curated content.
4. Tool outputs are reconciled into a final natural-language reply plus structured phone/event payloads.
5. Frontend receives streaming chunks, completes the assistant message, and maps structured events to phone cards and comparison tables.
6. Client stores session/context in local storage to persist history across refreshes while enforcing a 50-message cap.

## Data Pipeline
1. Fetch raw device records from RapidAPI (`mobile-phones2`).
2. Normalize, filter, and enrich the data via `backend/supabase_upload/data_upload.py`.
3. Load cleaned rows into Supabase Postgres (tables aligned with `backend/database.py` DTOs).
4. Runtime queries pull from Supabase to keep model responses grounded in factual specs.

To refresh the dataset:
```bash
export RAPIDAPI_KEY=your_key
export RAPIDAPI_HOST=mobile-phones2.p.rapidapi.com
python backend/supabase_upload/data_upload.py
```

## Prompt Design & Safety Strategy
- **Layered system prompts**: `agent_instructions.py` defines core persona, factual sourcing directives, refusal templates, and enumerated disallowed content categories (prompt leaks, secret requests, harassment).
- **Tool-usage constraints**: ADK planner explicitly describes each tool’s contract, forcing the model to ground answers in Supabase results rather than hallucinated specs.
- **Input sanitation & guardrails**: pre-checks flag adversarial strings (e.g., “ignore previous instructions”, “reveal API key”) and redirect the model to refusal verbiage.
- **Clarification routines**: missing constraints (budget, brand, quantity) trigger follow-up questions, reducing ambiguous or over-confident recommendations.
- **Safety responses**: agent returns neutral refusals for toxicity or brand defamation requests, citing policy instead of engaging.
- **Grounded reasoning**: comparison and explanation outputs include trace metadata so the frontend can render only devices mentioned, limiting hallucinated cards.
- **Session governance**: rolling 50-message cap and timeout guards prevent prompt inflation and long-running generations.

## Known Requirements Coverage
- Conversational recommendations with structured rationales.
- Comparison cards that list pros/cons, spec diffs, and price bands.
- Ability to filter by brand, budget, and features (fast charging, camera, etc.).
- Safety responses to adversarial prompts (prompt leak, API key, toxic language).
- Public deployment links for both frontend and backend.


## Project Layout
```
backend/
  agent.py               # Gemini chat orchestrator and tool router
  agent_instructions.py  # System prompts, safety and refusal templates
  api.py                 # FastAPI routes (/chat, /health)
  database.py            # Supabase client and DTO models
  tools.py               # Tool implementations for catalogue search/comparison
  supabase_upload/       # RapidAPI ingestion scripts and utilities
frontend/
  src/hooks/useChat.ts   # Chat state machine and request pipeline
  src/utils/phoneExtract.ts # Maps agent events to rendered phone cards
  ...                    # React components, styling, routing
requirements.txt         # Backend dependencies
README.md                # Project documentation (this file)
```

## Deployment Strategy

### Backend on Hugging Face Spaces
1. Push `backend/` to https://huggingface.co/spaces/nitin23329/mobile-shopping-agent-backend (Docker runtime).
2. Set secrets: `GOOGLE_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `RAPIDAPI_KEY`, `RAPIDAPI_HOST`, `API_REQUEST_TIMEOUT_SECONDS`.
3. Build logs confirm Uvicorn serving on port 7860; health endpoint is https://nitin23329-mobile-shopping-agent-backend.hf.space/health.
4. Swagger docs available at `/docs` for manual testing.

### Frontend on Vercel
1. Connect the repo and push the `frontend/` build output.
2. Configure environment variables: `VITE_API_BASE_URL=https://nitin23329-mobile-shopping-agent-backend.hf.space`.
3. `npm run build` produces static assets; Vercel deploys automatically.
4. Production URL: https://mobile-shopping-agent-frontend-nitin23329s-projects.vercel.app?_vercel_share=AI7h6MowlQKC9mhHUfshpdfKNpmBaZPf.

### Post-deploy checks
- Verify `/health` responds 200.
- Run smoke queries: budget recommendation, two-phone comparison, safety refusal.
- Confirm cards rendered match the textual recommendations (frontend uses reply text token matching for validation).


## Known Limitations
- Catalogue freshness depends on manual RapidAPI ingestions; pricing and availability are not updated in real time.
- Regional coverage is tuned for INR price bands; global currency or carrier-specific data is not modelled.
- User sessions live only in browser storage; no account system, syncing, or analytics pipeline is in place.
- Gemini-generated responses can still be verbose; without rate limiting, simultaneous heavy usage could hit Google ADK or Supabase quotas.
- Frontend/offline experience remains shallow (no PWA caching, limited accessibility audits).
- Automated testing is minimal; acceptance relies on manual smoke runs until Playwright/pytest suites are added.
