"""
Helpdesk AI — FastAPI Server
-----------------------------
REST API that bridges the frontend chat UI with the Gemini-powered agent.
"""

import os
import sys
import uuid
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

try:
    import agent
except ImportError:
    from backend import agent


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("Helpdesk AI server starting...")
    print("   Agent model :", agent.MODEL_NAME)
    print("   Tools loaded:", [t.__name__ for t in agent.TOOLS])
    yield
    print("Helpdesk AI server shutting down.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Helpdesk AI API",
    description="AI-powered IT helpdesk ticketing system using Gemini",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow local frontend origins
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        # file:// origin for opening HTML directly in browser
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class TicketRequest(BaseModel):
    """Incoming ticket message from the frontend."""
    message: str
    session_id: str | None = None


class TicketResponse(BaseModel):
    """Agent response sent back to the frontend."""
    response: str
    session_id: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "helpdesk-ai",
        "model": agent.MODEL_NAME,
    }


@app.post("/api/ticket", response_model=TicketResponse)
async def handle_ticket(request: TicketRequest):
    """
    Receive a user ticket message, route it through the Gemini agent,
    and return the agent's response.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Generate or reuse session ID for multi-turn conversations
    session_id = request.session_id or str(uuid.uuid4())

    try:
        response_text = agent.send_message(session_id, request.message.strip())
        return TicketResponse(response=response_text, session_id=session_id)
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(exc)}",
        )


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a conversation session."""
    removed = agent.clear_session(session_id)
    return {"cleared": removed, "session_id": session_id}
