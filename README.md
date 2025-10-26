git clone https://github.com/NITIN23329/mobile-shopping-agent.git
# Mobile Shopping Agent (Google ADK)

An end-to-end Gemini-powered shopping assistant built with the Google Agent Development Kit (ADK). The agent ingests a curated catalogue of mobile phones, answers natural-language queries, compares devices, and renders recommendations in a responsive React chat UI.

## Live Demo
- Frontend (Vercel): https://mobile-shopping-agent-frontend-nitin23329s-projects.vercel.app?_vercel_share=AI7h6MowlQKC9mhHUfshpdfKNpmBaZPf
- Backend API (Hugging Face Spaces): https://nitin23329-mobile-shopping-agent-backend.hf.space/ (Swagger docs at https://nitin23329-mobile-shopping-agent-backend.hf.space/docs)

## Feature Highlights
- Conversational search that extracts intent (budget, brand, key features) from free-form prompts.
- Comparison mode that contrasts two to three phones with structured spec cards and trade-off summaries.
- Explainable recommendations reasoned directly from Supabase-sourced catalogue facts.
- Safety guardrails that deflect adversarial prompts (prompt leakage, API key requests, toxic brand bashing).
- Mobile-first web interface with product cards, comparison table, and persistent session management.

## Architecture & Tech Stack
- **Frontend**: React + Vite (TypeScript), Tailwind CSS, Axios; deployed on Vercel.
- **Backend**: FastAPI, Google ADK, Gemini via LiteLLM, Supabase Python client, Pydantic; deployed on Hugging Face Spaces Docker runtime.
- **Data Layer**: Phone catalogue seeded from RapidAPI (`apikite/mobile-phones2`) into Supabase Postgres.
- **Tooling**: Conda (Python), Node.js ≥ 18, nvm, GitHub Actions-ready structure.

### High-level Flow
1. Users chat through the Vercel-hosted frontend.
2. The client calls the FastAPI `/chat` endpoint with session context.
3. The ADK agent orchestrates Gemini models plus custom tools:
   - Vector/text search in Supabase for phones matching parsed constraints.
   - Comparison tool assembling structured specs.
4. Server replies stream back to the frontend, which renders rich cards matching the textual response.

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
- **System instructions** (see `backend/agent_instructions.py`) reinforce neutral tone, sourcing from Supabase, and refuse unsafe requests.
- **Guardrail heuristics** detect attempts to reveal prompts, request secrets, or incite toxic content, returning controlled refusal messages.
- **Spec grounding**: model answers must reference catalogue facts; comparisons cite verifiable specs (battery, camera, chipset, price).
- **Ambiguity handling**: when the query lacks constraints, the agent asks clarifying questions before recommending.
- **Session memory**: lightweight history keeps context while enforcing a 50-message cap to avoid prompt bloat.

## Known Requirements Coverage
- Conversational recommendations with structured rationales.
- Comparison cards that list pros/cons, spec diffs, and price bands.
- Ability to filter by brand, budget, and features (fast charging, camera, etc.).
- Safety responses to adversarial prompts (prompt leak, API key, toxic language).
- Public deployment links for both frontend and backend.

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
cp .env.example .env.local  # if present
```

Populate `.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000
VITE_DEBUG_LOGGING=false
VITE_REQUEST_TIMEOUT_MS=120000
```

Run the dev server:
```bash
npm run dev -- --open
```

### Run frontend and backend together
- Terminal A: `conda activate mobile-shopping-agent && uvicorn backend.api:app --reload --port 8000`
- Terminal B: `cd frontend && npm run dev`

Visit http://127.0.0.1:5173/ to chat with the agent. Structured phone cards render beneath each agent reply.

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
1. Connect the repo or push the `frontend/` build output.
2. Configure environment variables: `VITE_API_BASE_URL=https://nitin23329-mobile-shopping-agent-backend.hf.space`.
3. `npm run build` produces static assets; Vercel deploys automatically.
4. Production URL: https://mobile-shopping-agent-frontend-nitin23329s-projects.vercel.app/.

### Post-deploy checks
- Verify `/health` responds 200.
- Run smoke queries: budget recommendation, two-phone comparison, safety refusal.
- Confirm cards rendered match the textual recommendations (frontend uses reply text token matching for validation).

## Testing & Validation
- Manual regression passes cover: recommendations under budget, explicit brand filter, 1:1 comparisons, safety refusal prompts.
- Frontend token matching ensures only phones mentioned in the reply render as cards.
- Pending automation: add Playwright smoke tests and backend pytest suite (tracked in TODOs).

## Known Limitations
- Reliant on periodic RapidAPI snapshots; specs may drift from the latest market releases.
- No persistent user authentication or personalized history beyond session storage.
- Safety heuristics handle common prompt injections but are not formally verified.
- Latency depends on Gemini response times; long comparisons may approach the 120s timeout.

## Troubleshooting
- **Import errors for Google ADK models**: ensure `google-genai` ≥ 1.46.0 and `websockets` ≥ 15.0.1 (already in `requirements.txt`).
- **Timeouts**: adjust `API_REQUEST_TIMEOUT_SECONDS` (backend) or `VITE_REQUEST_TIMEOUT_MS` (frontend) for longer-running calls.
- **CORS issues**: confirm the backend allows the Vercel origin in its CORS middleware configuration.
- **Dataset refresh failures**: check RapidAPI quota and Supabase service key permissions.

## License

MIT License. See `LICENSE` for details.
