# Mobile Shopping Agent — Frontend

Responsive chat UI for the Gemini-powered mobile shopping agent. Built with React, Vite, TypeScript, and Tailwind CSS. The interface lets shoppers ask conversational questions, view curated phone cards, and compare devices side by side.

## Quick Start

```bash
cd frontend
npm install
npm run dev -- --open
```

Set the backend URL in `.env.local` (create it if missing):

```
VITE_API_BASE_URL=http://localhost:8000
```

The dev server runs at <http://127.0.0.1:5173>. Requests are proxied to the FastAPI backend specified in `VITE_API_BASE_URL`.

## Scripts

| Command | Description |
| ------- | ----------- |
| `npm run dev` | Start Vite in development mode with HMR |
| `npm run build` | Type-check and bundle for production |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run eslint across the project |

## UI Highlights

- **Mobile-first chat** with sticky composer, optimistic updates, and clipboard support
- **Phone cards** showcasing pricing and spotlight specs extracted from the agent tool outputs
- **Comparison table** that auto-renders when the agent returns two to three phones
- **Raw response viewer** for debugging tool traces and structured data

## Folder Structure

```
frontend/
  src/
    api/            # HTTP client for the FastAPI /chat endpoint
    components/     # Reusable UI pieces (cards, bubbles, composer, etc.)
    hooks/          # Chat state management + local session persistence
    types/          # Shared TypeScript interfaces
    utils/          # Helpers for extracting phone metadata from raw events
```

## Deployment Notes

1. Build the static assets: `npm run build`
2. Deploy `dist/` (e.g., Vercel, Netlify, Cloudflare Pages)
3. Set `VITE_API_BASE_URL` in the hosting platform to point at the deployed FastAPI backend

## Troubleshooting

- **CORS errors**: ensure the FastAPI deployment allows the frontend origin.
- **Missing phone cards**: confirm the backend returns structured phone data in `raw_response.events`; the UI will gracefully fallback to text-only responses.
- **Clipboard unavailable**: some browsers block programmatic copy outside secure origins—use HTTPS in production.

## License

MIT — see the repository root for details.
