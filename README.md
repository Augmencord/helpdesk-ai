# 🤖 Helpdesk AI — Intelligent IT Support Ticketing System

An end-to-end AI-powered helpdesk ticketing system featuring a premium chat UI, a FastAPI backend, and a Gemini-powered agentic framework that classifies tickets, asks clarifying questions, and invokes the correct tools to resolve employee IT issues.

---

## 📸 Architecture

```
┌─────────────────────┐       HTTP POST        ┌──────────────────────────┐
│                     │  /api/ticket            │                          │
│   Frontend (Chat)   │ ──────────────────────▶ │   FastAPI Backend        │
│   HTML / CSS / JS   │                         │   (main.py)              │
│   Port 3000         │ ◀────────────────────── │   Port 8000              │
│                     │   JSON Response         │                          │
└─────────────────────┘                         └────────────┬─────────────┘
                                                             │
                                                             │ Sends user message
                                                             ▼
                                                ┌──────────────────────────┐
                                                │   Gemini Agent           │
                                                │   (agent.py)             │
                                                │                          │
                                                │   System Prompt +        │
                                                │   Stateful Chat Session  │
                                                │   + Auto Function Call   │
                                                └────────────┬─────────────┘
                                                             │
                                                             │ Invokes tools
                                                             ▼
                                                ┌──────────────────────────┐
                                                │   Tools / Skills         │
                                                │   (tools.py)             │
                                                │                          │
                                                │   • trigger_password_    │
                                                │     reset(username)      │
                                                │   • check_account_      │
                                                │     status(username)     │
                                                │   • get_leave_balance    │
                                                │     (employee_id)        │
                                                └──────────────────────────┘
```

---

## 📋 Prerequisites

| Requirement       | Version    | Notes                                         |
|--------------------|------------|-----------------------------------------------|
| **Python**         | 3.10+      | [Download](https://www.python.org/downloads/) |
| **pip**            | latest     | Comes with Python                             |
| **Web Browser**    | Any modern | Chrome, Edge, Firefox, Safari                 |
| **Gemini API Key** | —          | [Get one here](https://aistudio.google.com/apikey) |

---

## 🚀 Quick Start

### 1. Navigate to the Project Directory

```bash
cd helpdesk-ai
```

### 2. Set Up the Backend

#### a) Create a Python Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### b) Install Dependencies

```bash
pip install -r backend/requirements.txt
```

#### c) Configure Environment Variables

Copy the template and add your Gemini API key:

**Windows (PowerShell):**
```powershell
Copy-Item backend\.env.template backend\.env
```

**macOS / Linux:**
```bash
cp backend/.env.template backend/.env
```

Now open `backend/.env` in your editor and replace the placeholder:

```env
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

> ⚠️ **Important:** Never commit your `.env` file to version control. Add it to `.gitignore`.

#### d) Start the FastAPI Server

```bash
uvicorn backend.main:app --reload --port 8000
```

You should see output like:
```
🚀 Helpdesk AI server starting...
   Agent model : gemini-2.5-flash
   Tools loaded: ['trigger_password_reset', 'check_account_status', 'get_leave_balance']
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Verify the server is running:**
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status": "healthy", "service": "helpdesk-ai", "model": "gemini-2.5-flash"}
```

### 3. Start the Frontend

Open a **new terminal** (keep the backend running) and serve the frontend:

```bash
cd frontend
python -m http.server 5500
```

Then open your browser to: **http://localhost:5500**

> **Note:** Port 5500 (or 8080) can be used if port 3000 is already occupied by another service on your system. All of these ports (`3000`, `5500`, `8080`) are pre-configured in the FastAPI CORS middleware.
> **Alternative:** You can also directly open `frontend/index.html` in your browser. The CORS configuration supports the `null` origin for file:// URLs.

---

## 🎯 Testing the Three Ticket Types

Once both servers are running, try these queries in the chat:

### 1. Password Reset
```
I forgot my password, how to reset it?
```
→ The agent will ask for your **username**, then call `trigger_password_reset()` and return a mock reset link.

### 2. Login Issue
```
I can't login as password is incorrect
```
→ The agent will ask for your **username**, then call `check_account_status()` to check if your account is locked.

### 3. Leave Balance
```
How to see my leave balance?
```
→ The agent will ask for your **employee ID**, then call `get_leave_balance()` and return a detailed balance table.

### Multi-Turn Conversation
The agent maintains conversation context within a session. You can provide follow-up information naturally:

```
User: I forgot my password
Agent: I'd be happy to help! Could you please provide your username or email?
User: john.doe@company.com
Agent: ✅ Password reset initiated for john.doe@company.com! [reset link...]
```

---

## 📁 Project Structure

```
helpdesk-ai/
├── backend/
│   ├── main.py              # FastAPI server, CORS, /api/ticket endpoint
│   ├── agent.py             # Gemini agent config, system prompt, sessions
│   ├── tools.py             # Three custom tool functions
│   ├── requirements.txt     # Python dependencies
│   ├── .env.template        # Environment variable template
│   └── .env                 # Your actual API key (git-ignored)
├── frontend/
│   ├── index.html           # Chat UI structure
│   ├── style.css            # Premium dark-mode styling
│   └── app.js               # Frontend logic & API communication
└── README.md                # This file
```

---

## 🔧 Configuration

### CORS Origins

The backend allows requests from these origins (configured in `backend/main.py`):

| Origin                      | Use Case                           |
|-----------------------------|-------------------------------------|
| `http://localhost:3000`     | Python HTTP server                  |
| `http://127.0.0.1:3000`    | Python HTTP server (alt)            |
| `http://localhost:5500`     | VS Code Live Server                 |
| `http://127.0.0.1:5500`    | VS Code Live Server (alt)           |
| `http://localhost:8080`     | Alternative dev server              |
| `null`                      | Opening HTML file directly          |

### Environment Variables

| Variable          | Required | Description                      |
|-------------------|----------|----------------------------------|
| `GEMINI_API_KEY`  | ✅ Yes   | Your Google Gemini API key       |

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Cannot reach the server"** in frontend | Ensure the backend is running on port 8000 |
| **CORS errors** in browser console | Check that your frontend origin is in the CORS allow list |
| **"GEMINI_API_KEY is not set"** | Ensure you copied `.env.template` to `.env` and added your key |
| **Module not found errors** | Ensure you activated the virtual environment and ran `pip install` |
| **Agent returns errors** | Check the backend terminal for detailed error logs |

---

## 📄 API Reference

### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "service": "helpdesk-ai",
    "model": "gemini-2.5-flash"
}
```

### `POST /api/ticket`
Submit a helpdesk ticket message.

**Request Body:**
```json
{
    "message": "I forgot my password",
    "session_id": "sess_abc123"   // optional, auto-generated if omitted
}
```

**Response:**
```json
{
    "response": "I'd be happy to help you reset your password! ...",
    "session_id": "sess_abc123"
}
```

### `DELETE /api/session/{session_id}`
Clear a conversation session.

**Response:**
```json
{
    "cleared": true,
    "session_id": "sess_abc123"
}
```

---

## 📝 License

This project is for educational and demonstration purposes.
