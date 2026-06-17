"""
Romih Agent - Minimal Router
=============================
Lazy imports to avoid startup failures
"""
import sys
import os
import io
import json

# Path setup
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _BACKEND_DIR)
sys.path.insert(0, os.path.join(_BACKEND_DIR, "romih_agent"))

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/romih", tags=["Romih Agent"])

# Lazy-loaded agent - only initialized when first needed
_agent = None
_bot = None
_handler = None


def _get_agent():
    global _agent, _bot, _handler
    if _agent is None:
        from romih_agent.core.agent import RomihAgent, AgentConfig
        from romih_agent.server.telegram_bot import TelegramBot, MessageHandler
        _agent = RomihAgent(AgentConfig(name="محمد"))
        _bot = TelegramBot()
        _handler = MessageHandler(_agent)
    return _agent, _bot, _handler


class ChatRequest(BaseModel):
    message: str
    task_type: str = "chat"
    prefer_local: bool = False


# ═══ Simple test route ═══

@router.get("/ping")
async def ping():
    return {"status": "romih", "version": "v5.9", "tools": "178", "message": "Romih Agent is alive"}


@router.get("/health")
async def health():
    try:
        agent, bot, _ = _get_agent()
        return {
            "status": "ok",
            "agent": "Romih Agent",
            "tools": len(agent.tools.tools),
            "telegram": "active" if bot.me else "not configured",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/status")
async def status():
    agent, _, _ = _get_agent()
    return agent.get_status()


@router.post("/chat")
async def chat(req: ChatRequest):
    agent, _, _ = _get_agent()
    agent.config.prefer_local = req.prefer_local
    response = await agent.chat(req.message, req.task_type)
    return {"response": response, "status": agent.get_status()}


@router.post("/goal")
async def execute_goal(req: ChatRequest):
    agent, _, _ = _get_agent()
    response = await agent.execute_goal(req.message)
    return {"response": response, "status": agent.get_status()}


@router.get("/debug/prompt")
async def debug_prompt():
    agent, _, _ = _get_agent()
    return {"system_prompt": agent.system_prompt[:2000]}


@router.get("/dashboard/data")
async def dashboard_data(user_id: str = "", industry: str = "", user_name: str = ""):
    """Personalized dashboard — industry-specific cards and stats with name greeting"""
    from tools.dashboard_api import get_user_dashboard
    return get_user_dashboard(user_id, industry, user_name)


@router.get("/tools")
async def list_tools():
    agent, _, _ = _get_agent()
    return {"categories": agent.tools.list_by_category(), "total": len(agent.tools.tools)}


@router.get("/experts")
async def list_experts():
    from romih_agent.tools.rabie_brain import EXPERTS, METHODOLOGIES
    return {"experts": EXPERTS, "methodologies": METHODOLOGIES}


@router.post("/tools/execute")
async def execute_tool(req: dict):
    agent, _, _ = _get_agent()
    result = agent.tools.execute(
        req.get("tool_name", ""),
        req.get("params", {}),
        req.get("auto_approve", False)
    )
    return {"result": result}


@router.get("/memory")
async def get_memory():
    agent, _, _ = _get_agent()
    return agent.memory.long_term.get_stats() if agent.memory else {}


@router.get("/agents")
async def list_agents():
    agent, _, _ = _get_agent()
    if agent.swarm:
        return {"agents": agent.swarm.list_agents()}
    return {"agents": []}


# ═══ UI ═══

@router.get("/", response_class=HTMLResponse)
async def serve_ui():
    ui_path = os.path.join(_BACKEND_DIR, "romih_agent", "server", "ui.html")
    if not os.path.exists(ui_path):
        return HTMLResponse("<h1>UI not found</h1>")
    with open(ui_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return HTMLResponse(content=html, media_type="text/html; charset=utf-8")


@router.get("/download")
async def download_romih():
    """Redirect to GitHub download"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="https://github.com/saifromih-glitch/companies-hospital/archive/refs/heads/main.zip")


@router.get("/landing", response_class=HTMLResponse)
async def serve_landing():
    landing_path = os.path.join(_BACKEND_DIR, "romih_agent", "server", "landing.html")
    if not os.path.exists(landing_path):
        return HTMLResponse("<h1>Landing page not found</h1>")
    with open(landing_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return HTMLResponse(content=html, media_type="text/html; charset=utf-8")


@router.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    dashboard_path = os.path.join(_BACKEND_DIR, "romih_agent", "server", "dashboard.html")
    if not os.path.exists(dashboard_path):
        return HTMLResponse("<h1>Dashboard not found</h1>")
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return HTMLResponse(content=html, media_type="text/html; charset=utf-8")


# ═══ Telegram Webhook ═══

@router.post("/webhook")
async def telegram_webhook(req: Request):
    _, bot, handler = _get_agent()
    try:
        update = await req.json()
        msg = bot.parse_message(update)
        if msg and bot.token:
            await handler.handle(msg, bot)
    except Exception as e:
        print(f"Webhook error: {e}")
    return {"ok": True}


@router.get("/telegram/setup")
async def setup_telegram(webhook_url: str = ""):
    _, bot, _ = _get_agent()
    if not bot.token:
        return {"error": "TELEGRAM_BOT_TOKEN not set"}
    if not await bot.init():
        return {"error": "Invalid token"}
    if webhook_url:
        ok = await bot.set_webhook(f"{webhook_url}/romih/webhook")
        if ok:
            await bot.set_commands()
        return {"ok": ok, "webhook_url": f"{webhook_url}/romih/webhook", "bot": bot.me}
    return {"ok": True, "bot": bot.me}
