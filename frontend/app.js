/**
 * Helpdesk AI — Frontend Application Logic
 * ------------------------------------------
 * Manages chat interaction, API communication, session state,
 * message rendering, and UI animations.
 */

(() => {
    "use strict";

    // ── Configuration ──────────────────────────────────────────────────
    const API_BASE = "http://localhost:8000";
    const TICKET_ENDPOINT = `${API_BASE}/api/ticket`;
    const HEALTH_ENDPOINT = `${API_BASE}/api/health`;

    // ── State ──────────────────────────────────────────────────────────
    let sessionId = generateSessionId();
    let isProcessing = false;

    // ── DOM Elements ───────────────────────────────────────────────────
    const messagesList    = document.getElementById("messages-list");
    const chatContainer   = document.getElementById("chat-container");
    const inputForm       = document.getElementById("input-form");
    const messageInput    = document.getElementById("message-input");
    const btnSend         = document.getElementById("btn-send");
    const btnNewSession   = document.getElementById("btn-new-session");
    const typingIndicator = document.getElementById("typing-indicator");
    const quickActions    = document.getElementById("quick-actions");
    const statusDot       = document.getElementById("status-dot");
    const statusText      = document.getElementById("status-text");
    const toastContainer  = document.getElementById("toast-container");

    // ── Initialisation ─────────────────────────────────────────────────
    function init() {
        inputForm.addEventListener("submit", handleSubmit);
        btnNewSession.addEventListener("click", startNewSession);
        messageInput.addEventListener("input", autoResizeTextarea);
        messageInput.addEventListener("keydown", handleKeyDown);

        // Quick-action chips
        document.querySelectorAll(".chip").forEach(chip => {
            chip.addEventListener("click", () => {
                const msg = chip.getAttribute("data-message");
                if (msg) sendMessage(msg);
            });
        });

        checkBackendHealth();
        messageInput.focus();
    }

    // ── Session Management ─────────────────────────────────────────────
    function generateSessionId() {
        return "sess_" + crypto.randomUUID();
    }

    function startNewSession() {
        sessionId = generateSessionId();

        // Clear all messages except welcome
        const messages = messagesList.querySelectorAll(".message:not(.welcome-message)");
        messages.forEach(msg => msg.remove());

        // Show quick actions again
        quickActions.classList.remove("hidden");

        messageInput.value = "";
        autoResizeTextarea();
        messageInput.focus();

        showToast("New conversation started", "success");
    }

    // ── Message Sending ────────────────────────────────────────────────
    function handleSubmit(e) {
        e.preventDefault();
        const text = messageInput.value.trim();
        if (!text || isProcessing) return;
        sendMessage(text);
    }

    async function sendMessage(text) {
        if (isProcessing) return;
        isProcessing = true;

        // Clear input
        messageInput.value = "";
        autoResizeTextarea();
        btnSend.disabled = true;

        // Hide quick actions after first message
        quickActions.classList.add("hidden");

        // Render user bubble
        appendMessage(text, "user");

        // Show typing indicator
        showTyping(true);

        try {
            const res = await fetch(TICKET_ENDPOINT, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text, session_id: sessionId }),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: "Unknown error" }));
                throw new Error(err.detail || `Server error (${res.status})`);
            }

            const data = await res.json();
            sessionId = data.session_id || sessionId;

            showTyping(false);
            appendMessage(data.response, "ai");

        } catch (err) {
            showTyping(false);
            console.error("API Error:", err);

            if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
                showToast("Cannot reach the server. Is the backend running on port 8000?", "error");
                setOnlineStatus(false);
            } else {
                showToast(err.message, "error");
            }

            appendMessage(
                "⚠️ Sorry, I encountered an error processing your request. Please try again or check that the backend server is running.",
                "ai"
            );
        } finally {
            isProcessing = false;
            btnSend.disabled = false;
            messageInput.focus();
        }
    }

    // ── Message Rendering ──────────────────────────────────────────────
    function appendMessage(text, role) {
        const wrapper = document.createElement("div");
        wrapper.className = `message ${role}-message`;

        const avatar = document.createElement("div");
        avatar.className = `message-avatar ${role}-avatar`;
        avatar.setAttribute("aria-hidden", "true");

        if (role === "ai") {
            avatar.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>`;
        } else {
            avatar.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                </svg>`;
        }

        const content = document.createElement("div");
        content.className = "message-content";

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";
        bubble.innerHTML = formatMessage(text);

        const time = document.createElement("div");
        time.className = "message-time";
        time.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

        content.appendChild(bubble);
        content.appendChild(time);

        wrapper.appendChild(avatar);
        wrapper.appendChild(content);

        messagesList.appendChild(wrapper);
        scrollToBottom();
    }

    /**
     * Convert plain text / basic markdown to HTML.
     * Handles: **bold**, `code`, ```code blocks```, newlines, links, and lists.
     */
    function formatMessage(text) {
        if (!text) return "<p>No response received.</p>";

        let html = escapeHtml(text);

        // Code blocks (```)
        html = html.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");

        // Inline code
        html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

        // Bold
        html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

        // Italic
        html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

        // Links — detect URLs
        html = html.replace(
            /(https?:\/\/[^\s<]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );

        // Convert newlines to paragraphs / line breaks
        const paragraphs = html.split(/\n{2,}/);
        html = paragraphs
            .map(p => {
                const trimmed = p.trim();
                if (!trimmed) return "";
                // Convert single newlines within a paragraph to <br>
                return `<p>${trimmed.replace(/\n/g, "<br>")}</p>`;
            })
            .filter(Boolean)
            .join("");

        return html || "<p>No response received.</p>";
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    // ── Typing Indicator ───────────────────────────────────────────────
    function showTyping(show) {
        typingIndicator.hidden = !show;
        if (show) scrollToBottom();
    }

    // ── Scroll ─────────────────────────────────────────────────────────
    function scrollToBottom() {
        requestAnimationFrame(() => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        });
    }

    // ── Textarea Auto-Resize ───────────────────────────────────────────
    function autoResizeTextarea() {
        messageInput.style.height = "auto";
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
    }

    function handleKeyDown(e) {
        // Enter to send (Shift+Enter for new line)
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            inputForm.requestSubmit();
        }
    }

    // ── Health Check ───────────────────────────────────────────────────
    async function checkBackendHealth() {
        try {
            const res = await fetch(HEALTH_ENDPOINT, { method: "GET" });
            if (res.ok) {
                setOnlineStatus(true);
            } else {
                setOnlineStatus(false);
            }
        } catch {
            setOnlineStatus(false);
        }
    }

    function setOnlineStatus(online) {
        if (online) {
            statusDot.classList.remove("offline");
            statusText.textContent = "Online";
        } else {
            statusDot.classList.add("offline");
            statusText.textContent = "Offline";
        }
    }

    // ── Toast Notifications ────────────────────────────────────────────
    function showToast(message, type = "error") {
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        toast.textContent = message;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.add("removing");
            toast.addEventListener("animationend", () => toast.remove());
        }, 4000);
    }

    // ── Boot ───────────────────────────────────────────────────────────
    init();
})();
