"""FastAPI wrapper for the mobile shopping agent."""
import asyncio
import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

try:
    from .agent import agent
except ImportError:  # pragma: no cover
    from agent import agent  # type: ignore

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types


APP_NAME = "mobile-shopping-agent"
DEFAULT_USER_ID = "default-user"
API_REQUEST_TIMEOUT_SECONDS = 60.0
AGENT_RUN_TIMEOUT_SECONDS = API_REQUEST_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)

session_service = InMemorySessionService()
runner = Runner(
    agent=agent,
    app_name=APP_NAME,
    session_service=session_service,
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: Optional[str]
    message: str
    history: Optional[List[Message]] = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    raw_response: Dict[str, Any]


app = FastAPI(title="Mobile Shopping Agent API", version="0.1.0")


async def _ensure_session(session_id: Optional[str]) -> str:
    """Return an existing session ID or create a new session on demand."""
    cleaned_session_id = session_id.strip() if session_id else None

    if cleaned_session_id:
        existing_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=DEFAULT_USER_ID,
            session_id=cleaned_session_id,
        )
        if existing_session:
            logger.debug("Reusing existing session %s", cleaned_session_id)
            return cleaned_session_id

    created_session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=DEFAULT_USER_ID,
        session_id=cleaned_session_id,
    )
    logger.debug(
        "Created new session %s (requested=%s)",
        created_session.id,
        cleaned_session_id,
    )
    return created_session.id


def _extract_text_from_event_content(event_content: Optional[genai_types.Content]) -> str:
    if not event_content or not getattr(event_content, "parts", None):
        return ""
    text_chunks: List[str] = []
    for part in event_content.parts or []:
        text_part = getattr(part, "text", None)
        if text_part:
            text_chunks.append(text_part)
    return "".join(text_chunks).strip()


def _is_final_response(event: Any) -> bool:
    marker = getattr(event, "is_final_response", None)
    if callable(marker):
        try:
            return bool(marker())
        except Exception:  # noqa: BLE001
            return False
    return bool(marker)


def _extract_reply_from_events(events: List[Any]) -> str:
    for event in reversed(events):
        if _is_final_response(event):
            reply = _extract_text_from_event_content(getattr(event, "content", None))
            if reply:
                return reply

    for event in reversed(events):
        if getattr(event, "author", None) != "user":
            reply = _extract_text_from_event_content(getattr(event, "content", None))
            if reply:
                return reply
    return ""


async def _collect_agent_events(
    session_id: str,
    user_message: genai_types.Content,
    user_id: str = DEFAULT_USER_ID,
) -> List[Any]:
    events: List[Any] = []

    async def _consume() -> None:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            events.append(event)

    try:
        await asyncio.wait_for(_consume(), timeout=API_REQUEST_TIMEOUT_SECONDS)
    except asyncio.TimeoutError as exc:
        logger.error(
            "Agent run timed out for session %s after %.1f seconds",
            session_id,
            API_REQUEST_TIMEOUT_SECONDS,
        )
        raise HTTPException(status_code=504, detail="Agent execution timed out.") from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Agent execution failed for session %s", session_id)
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}") from exc

    logger.debug("Agent produced %d events for session %s", len(events), session_id)
    return events


@app.get("/health", tags=["health"])
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    message = (payload.message or "").strip()
    if not message:
        logger.warning(
            "Rejected empty message (session=%s, history_items=%d)",
            payload.session_id,
            len(payload.history or []),
        )
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    logger.info("Chat request payload: %s", payload.model_dump())

    session_id = await _ensure_session(payload.session_id)

    user_message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=message)],
    )

    events = await _collect_agent_events(session_id=session_id, user_message=user_message)

    reply = _extract_reply_from_events(events)

    logger.info("Agent reply (session=%s): %s", session_id, reply)

    serialized_events: List[Any] = []
    for event in events:
        if hasattr(event, "model_dump"):
            try:
                serialized_events.append(event.model_dump(mode="json"))
                continue
            except Exception:  # noqa: BLE001
                pass
        serialized_events.append(jsonable_encoder(event))

    raw_response = jsonable_encoder({"events": serialized_events})

    logger.debug("Raw agent response (session=%s): %s", session_id, raw_response)

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        raw_response=raw_response,
    )
