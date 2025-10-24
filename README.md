# Mobile Shopping Agent (Google ADK)

Gemini-powered shopping assistant built with the Google Agent Development Kit (ADK). The agent can search, compare, and explain mobile phones using a curated catalogue of realistic specs.

## What You Get
- Hierarchical agent system with a routing agent and three specialized sub-agents (shopping, recommendation, comparison)
- Five ADK tools for search, lookup, comparison, and feature explanations backed by a mock database
- Google Gemini (via LiteLLM) configured to use the `gemini-2.5-flash` model with Google AI Studio API keys
- ADK Web experience for conversational testing out of the box

## Requirements
- macOS, Linux, or Windows
- Python 3.11 (conda recommended for parity with development environment)
- Google AI Studio API key with access to Gemini 2.5 models

## Setup on a Fresh Machine
1. **Clone and enter the project**
	```bash
	git clone https://github.com/NITIN23329/mobile-shopping-agent.git
	cd mobile-shopping-agent
	```
2. **Create the Python environment** (optional but recommended)
	```bash
	conda create -n mobile-shopping-agent python=3.11
	conda activate mobile-shopping-agent
	```
3. **Install dependencies**
	```bash
	pip install -r requirements.txt
	```
4. **Configure credentials**
	- Create a file named `.env` in the project root
	- Add your Google AI Studio key: `GOOGLE_API_KEY=your_key_here`
	- Never commit `.env`; it should remain local only
5. **Launch the ADK web experience**
	```bash
	conda activate mobile-shopping-agent  # ensure the env is active
	adk web
	```
	The UI runs at `http://127.0.0.1:8000`. Select the backend app and start chatting.

## Project Layout
```
backend/
  agent.py               # Root agent plus sub-agent wiring and model bootstrap
  agent_instructions.py  # Prompt definitions for all agents
  tools.py               # ADK tool implementations backed by the mock database
  database.py            # Static phone catalogue used by the tools
requirements.txt         # Minimal dependency set (ADK, Gemini client, LiteLLM, dotenv)
```

## Typical Workflow
- Start ADK web and submit queries such as:
  - "Best camera phone under 30000"
  - "Compare Pixel 8a vs OnePlus 12R"
  - "Explain OIS vs EIS"
- The root agent detects intent and forwards the request to the appropriate specialist
- Tools fetch structured data from `database.py`; responses are composed by Gemini

## Customisation Tips
- Update `backend/database.py` to add or modify phone entries
- Adjust prompts in `backend/agent_instructions.py` to tune agent tone and behaviour
- Extend `backend/tools.py` with new functions and register them on the relevant agents in `backend/agent.py`

## Troubleshooting
- **LiteLLM still tries Vertex AI**: confirm `custom_llm_provider="gemini"` and `model="gemini-2.5-flash"` in `backend/agent.py`
- **Invalid API key**: verify the key works using a quick script (see Google AI Studio docs) and ensure `.env` is loaded before running `adk web`
- **Missing dependencies**: re-run `pip install -r requirements.txt` inside the active environment

## License
MIT License. See `LICENSE` for details.
