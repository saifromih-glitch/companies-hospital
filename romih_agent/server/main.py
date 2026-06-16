"""
Romih Agent - Web Server
=========================
FastAPI backend serving the UI + API
"""
import sys
import os
import io
import json
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from core.agent import RomihAgent, AgentConfig

# Telegram Bot
from server.telegram_bot import TelegramBot, MessageHandler

app = FastAPI(title="Romih Agent", version="1.0.0")

# الوكيل الرئيسي - يبدأ مرة واحدة
agent = RomihAgent(AgentConfig(name="محمد"))

# Telegram Bot
bot = TelegramBot()
handler = MessageHandler(agent)


class ChatRequest(BaseModel):
    message: str
    task_type: str = "chat"
    prefer_local: bool = False


class ToolRequest(BaseModel):
    tool_name: str
    params: dict = {}
    auto_approve: bool = False


# ═══ API Routes ═══

@app.get("/api/status")
async def status():
    return agent.get_status()


@app.post("/api/chat")
async def chat(req: ChatRequest):
    agent.config.prefer_local = req.prefer_local
    response = await agent.chat(req.message, req.task_type)
    return {"response": response, "status": agent.get_status()}


@app.get("/api/tools")
async def list_tools():
    return {
        "categories": agent.tools.list_by_category(),
        "total": len(agent.tools.tools)
    }


@app.get("/api/experts")
async def list_experts():
    from tools.rabie_brain import EXPERTS, METHODOLOGIES
    return {"experts": EXPERTS, "methodologies": METHODOLOGIES}


@app.post("/api/tools/execute")
async def execute_tool(req: ToolRequest):
    result = agent.tools.execute(req.tool_name, req.params, req.auto_approve)
    return {"result": result}


@app.get("/api/memory")
async def get_memory():
    return agent.memory.long_term.get_stats() if agent.memory else {}


@app.get("/api/agents")
async def list_agents():
    if agent.swarm:
        return {"agents": agent.swarm.list_agents()}
    return {"agents": []}


@app.post("/api/agents/delegate")
async def delegate_agent(req: dict):
    if agent.swarm:
        result = await agent.swarm.delegate(req["agent"], req["task"])
        return {"result": result}
    return {"error": "Swarm not available"}


# ═══ UI ═══

def ae(text: str) -> str:
    """Arabic to HTML entities - مضمون في أي بيئة"""
    return ''.join(f'&#{ord(c)};' if ord(c) > 127 else c for c in text)


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    ui_path = os.path.join(os.path.dirname(__file__), "ui.html")
    with open(ui_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return HTMLResponse(content=html, media_type="text/html; charset=utf-8")


@app.get("/api/health")
async def health():
    bot_status = "active" if bot.me else "not configured"
    return {
        "status": "ok",
        "agent": "Romih Agent",
        "tools": len(agent.tools.tools),
        "telegram": bot_status,
    }


# ═══ Telegram Webhook ═══

@app.post("/webhook/telegram")
async def telegram_webhook(req: Request):
    """Webhook endpoint for Telegram"""
    try:
        update = await req.json()
        msg = TelegramBot.parse_message(update)
        if msg and bot.token:
            await handler.handle(msg, bot)
    except Exception as e:
        print(f"Webhook error: {e}")
    return {"ok": True}


@app.get("/api/telegram/setup")
async def setup_telegram(webhook_url: str = ""):
    """Setup Telegram bot webhook"""
    if not bot.token:
        return {"error": "TELEGRAM_BOT_TOKEN not set"}

    if not await bot.init():
        return {"error": "Invalid token"}

    if webhook_url:
        webhook_url = webhook_url.rstrip("/") + "/webhook/telegram"
        ok = await bot.set_webhook(webhook_url)
        if ok:
            await bot.set_commands()
        return {"ok": ok, "webhook_url": webhook_url, "bot": bot.me}

    return {"ok": True, "bot": bot.me, "note": "Add ?webhook_url=YOUR_URL to set webhook"}


# ═══ Startup ═══

@app.on_event("startup")
async def startup():
    """تهيئة البوت عند بدء التشغيل"""
    if bot.token:
        if await bot.init():
            print(f"🤖 Telegram Bot: @{bot.me.get('username', 'unknown')} - ready")
            webhook_url = os.environ.get("WEBHOOK_URL", "")
            if webhook_url:
                await bot.set_webhook(f"{webhook_url}/webhook/telegram")
                await bot.set_commands()
                print(f"📡 Webhook set: {webhook_url}/webhook/telegram")
        else:
            print("⚠️ Telegram Bot: invalid token")
    else:
        print("ℹ️ Telegram Bot: no token (set TELEGRAM_BOT_TOKEN)")


if __name__ == "__main__":
    print("🌸 Romih Agent Server - http://localhost:8700")
    uvicorn.run(app, host="0.0.0.0", port=8700, log_level="info")
