# Mobile Shopping Agent (Google ADK)

Gemini-powered shopping assistant built with the Google Agent Development Kit (ADK). The agent can search, compare, and explain mobile phones using a curated catalogue of realistic specs. A lightweight React frontend (planned under `frontend/`) will provide the public chat experience, while the FastAPI backend stays in Python.

## Tech Stack
- **Backend**: FastAPI, Google ADK, Google Gemini via LiteLLM, Supabase Python client, Pydantic
- **Frontend**: React + Vite (TypeScript), Tailwind CSS (or CSS modules), Axios/fetch for API calls *(scaffolding forthcoming)*
- **Tooling**: Conda for Python env management, Node.js (LTS) for the frontend build, GitHub for code hosting/deployment workflows

## Requirements

| Purpose | Tooling |
| ------- | ------- |
| Backend | Python 3.11, Conda (recommended), pip, Supabase service key, Google AI Studio API key |
| Frontend | Node.js ≥ 18 (LTS), npm or pnpm, modern browser |
| Shared | macOS/Linux/Windows, Git |

### Installing Node.js alongside Conda

The Python/Conda environment is untouched by Node, so you can install Node with any preferred method. Using `nvm` keeps versions isolated:

```bash
# install nvm (see https://github.com/nvm-sh/nvm#installing-and-updating)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# load nvm in your current shell (or reopen terminal)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# install Node LTS and set as default
nvm install --lts
nvm use --lts
```

Verify installation:

```bash
node -v   # should print >= 18.x
npm -v
```

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/NITIN23329/mobile-shopping-agent.git
cd mobile-shopping-agent
```

### 2. Backend setup (FastAPI + Google ADK)

```bash
conda create -n mobile-shopping-agent python=3.11  # once
conda activate mobile-shopping-agent
pip install -r requirements.txt
```

Create `.env` at the project root and add:

```
GOOGLE_API_KEY=your_google_ai_studio_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_or_anon_key
```

Run the API locally:

```bash
uvicorn backend.app:app --reload --port 8000
# health check: curl http://localhost:8000/health
```

### 3. Frontend setup (React + Vite)

> The `frontend/` scaffold will live beside `backend/`. Once generated:

```bash
cd frontend
npm install
cp .env.example .env.local  # if provided
```

Add your backend URL to `.env.local` (during local dev this will be `http://localhost:8000`):

```
VITE_API_BASE_URL=http://localhost:8000
```

Start the dev server:

```bash
npm run dev -- --open
```

The frontend will proxy requests to the FastAPI backend using the configured base URL.

### 4. Running both together

- Terminal A: `conda activate mobile-shopping-agent && uvicorn backend.api:app --reload --port 8000`
- Terminal B: `cd frontend && npm run dev`

Open the frontend UI (default `http://127.0.0.1:5173/`) and start chatting. The frontend includes product cards and comparison layouts to visualize structured replies from the agent.

## Project Layout

```
backend/
	agent.py               # Root agent plus sub-agent wiring and model bootstrap
	agent_instructions.py  # Prompt definitions for all agents
	tools.py               # ADK tool implementations backed by Supabase
	database.py            # Supabase client integration and DTOs
frontend/                # React + Vite app (created in upcoming steps)
requirements.txt         # Backend Python dependencies
README.md                # You are here
```

## Deployment Overview

1. **Backend (FastAPI)**
	 - Containerize with Docker or deploy directly to services like Render, Fly.io, Google Cloud Run, or Azure Web Apps.
	 - Expose `/health` and `/chat` endpoints over HTTPS.
	 - Set `GOOGLE_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY` in the platform’s secret manager.
	 - Enable CORS for your frontend origin.

2. **Frontend (Vite build output)**
	 - Run `npm run build` to emit static assets in `frontend/dist`.
	 - Deploy to Vercel, Netlify, Cloudflare Pages, or GitHub Pages.
	 - Configure the `VITE_API_BASE_URL` environment variable to point at the hosted backend.

3. **Verification**
	 - Smoke test `https://<backend>/health`.
	 - From the hosted frontend, send sample queries (recommendations, comparisons, feature explanations).

## Customisation Tips
- Update `backend/database.py` or the underlying Supabase table to add/modify phone entries.
- Adjust prompts in `backend/agent_instructions.py` to tune agent tone, routing, or guardrails.
- Extend `backend/tools.py` with additional Supabase queries or third-party integrations.
- On the frontend, tweak card layouts, add filters, or integrate analytics/tracking as needed.

## Troubleshooting
- **Import errors for Google ADK models**: ensure `google-genai` ≥ 1.46.0 and `websockets` ≥ 15.0.1 (already declared in `requirements.txt`).
- **FastAPI logs show timeouts**: the API enforces a 60-second timeout per request; long-running model calls will return HTTP 504.
- **CORS errors in the browser**: confirm the backend deployment allows the frontend origin in its CORS configuration.
- **Missing Node tooling**: rerun `nvm use --lts` or install Node from https://nodejs.org if you prefer a system-wide installer.

## License

MIT License. See `LICENSE` for details.
