# -*- coding: utf-8 -*-
"""Gmail tools for Romih Agent via Maton API gateway."""
import os, json, httpx
from tools.registry import Tool, RiskLevel, ToolParam

MATON_KEY = os.environ.get("MATON_API_KEY", "")
MATON_URL = "https://gateway.maton.ai/google-mail/gmail/v1"


def _maton(path: str, method: str = "GET", data: dict = None, params: dict = None):
    """Proxy call to Maton Gmail gateway"""
    if not MATON_KEY:
        return {"error": "MATON_API_KEY not set. Set it as environment variable."}
    try:
        headers = {"Authorization": f"Bearer {MATON_KEY}"}
        url = f"{MATON_URL}/{path.lstrip('/')}"
        if method == "GET":
            r = httpx.get(url, headers=headers, params=params, timeout=15)
        elif method == "POST":
            r = httpx.post(url, headers=headers, json=data, timeout=15)
        elif method == "DELETE":
            r = httpx.delete(url, headers=headers, timeout=15)
        else:
            return {"error": f"Unsupported method: {method}"}
        return {"ok": True, "data": r.json()} if r.status_code < 400 else {"ok": False, "error": r.text[:200], "status": r.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def register(tools_registry):
    tools_registry.register(Tool(
        name="gmail_list",
        description="List recent Gmail messages. Optional: q=is:unread to filter",
        category="email",
        risk=RiskLevel.MEDIUM,
        params=[
            ToolParam(name="max_results", type="number", description="Max messages (default 10)", required=False),
            ToolParam(name="query", type="string", description="Filter: is:unread, from:email, subject:word etc", required=False)
        ],
        execute=lambda max_results=10, query="", **_: _maton(
            f"users/me/messages", "GET", params={"maxResults": max_results, "q": query}
        )
    ))

    tools_registry.register(Tool(
        name="gmail_read",
        description="Read a specific Gmail message by ID",
        category="email",
        risk=RiskLevel.MEDIUM,
        params=[ToolParam(name="message_id", type="string", description="Gmail message ID", required=True)],
        execute=lambda message_id, **_: _maton(f"users/me/messages/{message_id}", "GET")
    ))

    tools_registry.register(Tool(
        name="gmail_send",
        description="Send an email via Gmail",
        category="email",
        risk=RiskLevel.HIGH,
        params=[
            ToolParam(name="to", type="string", description="Recipient email", required=True),
            ToolParam(name="subject", type="string", description="Email subject", required=True),
            ToolParam(name="body", type="string", description="Email body (plain text or HTML)", required=True)
        ],
        execute=lambda to, subject, body, **_: _send_email(to, subject, body)
    ))

    tools_registry.register(Tool(
        name="gmail_search",
        description="Search Gmail messages with query",
        category="email",
        risk=RiskLevel.MEDIUM,
        params=[
            ToolParam(name="query", type="string", description="Search: is:unread, from:email, subject:word", required=True),
            ToolParam(name="max_results", type="number", description="Max messages (default 20)", required=False)
        ],
        execute=lambda query, max_results=20, **_: _maton(
            f"users/me/messages", "GET", params={"maxResults": max_results, "q": query}
        )
    ))

    tools_registry.register(Tool(
        name="gmail_profile",
        description="Get Gmail account profile info",
        category="email",
        risk=RiskLevel.LOW,
        params=[],
        execute=lambda **_: _maton("users/me/profile", "GET")
    ))

    print(f"Gmail: 5 tools registered (list, read, send, search, profile)")


def _send_email(to: str, subject: str, body: str) -> dict:
    """Send email using Gmail API raw format"""
    from email.mime.text import MIMEText
    import base64

    msg = MIMEText(body, "plain", "utf-8")
    msg["To"] = to
    msg["Subject"] = subject

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return _maton("users/me/messages/send", "POST", data={"raw": raw})
