"""
Helpdesk AI Agent
-----------------
Configures the Gemini-powered agent with system instructions,
registers custom tools, and manages per-session chat state.
"""

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

from tools import trigger_password_reset, check_account_status, get_leave_balance

# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Copy .env.template to .env and add your key."
    )

MODEL_NAME = "gemini-2.5-flash"

# ---------------------------------------------------------------------------
# System instruction for the Helpdesk Agent
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """You are an expert IT Helpdesk Support Agent. Your role is to help employees resolve their IT issues quickly and professionally.

## Your Capabilities
You have access to three tools:
1. **trigger_password_reset** — Sends a password reset link to a user.
2. **check_account_status** — Checks if a user's account is locked or has login issues.
3. **get_leave_balance** — Retrieves an employee's leave/PTO balance.

## Workflow
1. **Greet** the user warmly and acknowledge their issue.
2. **Classify** the ticket into one of these categories:
   - **Password Reset**: User forgot their password and needs a reset link.
   - **Login Issue**: User cannot log in (incorrect password, locked account, etc.).
   - **Leave Balance Inquiry**: User wants to check their remaining leave/PTO.
3. **Ask for required information** before invoking any tool:
   - For password reset → ask for their **username or email**.
   - For login issues → ask for their **username or email**.
   - For leave balance → ask for their **employee ID**.
4. **Invoke the correct tool** with the information provided.
5. **Format a clear, helpful response** with the tool's output, adding any relevant advice.

## Guidelines
- Be concise, friendly, and professional.
- If the user's request doesn't match any of the three categories, politely explain what you can help with and suggest they contact the IT support team directly for other issues.
- If the user provides their username or employee ID upfront, skip the asking step and invoke the tool directly.
- Always confirm the action taken and offer further assistance.
- Format responses with clear structure using line breaks for readability.
"""

# ---------------------------------------------------------------------------
# Tool list
# ---------------------------------------------------------------------------
TOOLS = [trigger_password_reset, check_account_status, get_leave_balance]

# ---------------------------------------------------------------------------
# Gemini client (singleton)
# ---------------------------------------------------------------------------
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """Lazily initialise and return the Gemini client."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------
# In-memory store: session_id → Chat object
_sessions: dict[str, object] = {}


def get_or_create_session(session_id: str):
    """Return an existing chat session or create a new one.

    Each session maintains its own conversation history so the agent
    can ask follow-up questions and remember context.
    """
    if session_id not in _sessions:
        client = _get_client()
        chat = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=TOOLS,
                temperature=0.3,  # Low temperature for deterministic helpdesk responses
            ),
        )
        _sessions[session_id] = chat
    return _sessions[session_id]


def send_message(session_id: str, user_message: str) -> str:
    """Send a user message to the agent and return the text response.

    The chat session handles automatic function calling — if the model
    decides to invoke a tool, the SDK executes it and feeds the result
    back until a final text response is produced.
    """
    chat = get_or_create_session(session_id)
    response = chat.send_message(user_message)
    return response.text


def clear_session(session_id: str) -> bool:
    """Remove a session from the in-memory store."""
    return _sessions.pop(session_id, None) is not None
