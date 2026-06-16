"""
Romih Agent — FastAPI Router
=============================
Mounted inside Companies Hospital backend
Routes: /romih/* and /webhook/telegram
"""
import sys
import os
import io

# Path setup — romih_agent modules use relative imports
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _BACKEND_DIR)
sys.path.insert(0, os.path.join(_BACKEND_DIR, "romih_agent"))

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from romih_agent.core.agent import RomihAgent, AgentConfig
from romih_agent.server.telegram_bot import TelegramBot, MessageHandler

# Init agent once
agent = RomihAgent(AgentConfig(name="محمد"))
bot = TelegramBot()
handler = MessageHandler(agent)

router = APIRouter(prefix="/romih", tags=["Romih Agent"])


class ChatRequest(BaseModel):
    message: str
    task_type: str = "chat"
    prefer_local: bool = False


# ═══ API Routes ═══

@router.get("/health")
async def health():
    return {
        "status": "ok",
        "agent": "Romih Agent",
        "tools": len(agent.tools.tools),
        "telegram": "active" if bot.me else "not configured",
    }

@router.get("/status")
async def status():
    return agent.get_status()

@router.post("/chat")
async def chat(req: ChatRequest):
    agent.config.prefer_local = req.prefer_local
    response = await agent.chat(req.message, req.task_type)
    return {"response": response, "status": agent.get_status()}

@router.get("/tools")
async def list_tools():
    return {"categories": agent.tools.list_by_category(), "total": len(agent.tools.tools)}

@router.get("/experts")
async def list_experts():
    from romih_agent.tools.rabie_brain import EXPERTS, METHODOLOGIES
    return {"experts": EXPERTS, "methodologies": METHODOLOGIES}

@router.post("/tools/execute")
async def execute_tool(req: dict):
    result = agent.tools.execute(req.get("tool_name",""), req.get("params",{}), req.get("auto_approve",False))
    return {"result": result}

@router.get("/memory")
async def get_memory():
    return agent.memory.long_term.get_stats() if agent.memory else {}

@router.get("/agents")
async def list_agents():
    if agent.swarm:
        return {"agents": agent.swarm.list_agents()}
    return {"agents": []}


# ═══ UI ═══

@router.get("/", response_class=HTMLResponse)
async def serve_ui():
    ui_path = os.path.join(os.path.dirname(__file__), "romih_agent", "server", "ui.html")
    with open(ui_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return HTMLResponse(content=html, media_type="text/html; charset=utf-8")


# ═══ Telegram Webhook ═══

@router.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        update = await req.json()
        msg = TelegramBot.parse_message(update)
        if msg and bot.token:
            await handler.handle(msg, bot)
    except Exception as e:
        print(f"Webhook error: {e}")
    return {"ok": True}


@router.get("/telegram/setup")
async def setup_telegram(webhook_url: str = ""):
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


# ═══ Startup ═══

@router.on_event("startup")
async def startup():
    if bot.token:
        if await bot.init():
            print(f"🤖 Telegram Bot: @{bot.me.get('username', 'unknown')} — ready")
            webhook_url = os.environ.get("WEBHOOK_URL", "")
            if webhook_url:
                await bot.set_webhook(f"{webhook_url}/romih/webhook")
                await bot.set_commands()
                print(f"📡 Webhook set: {webhook_url}/romih/webhook")
