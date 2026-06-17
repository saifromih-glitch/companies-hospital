# -*- coding: utf-8 -*-
"""
Romih Agent - Local Install
============================
Like AutoClaw: one command, everything runs.
  • Web UI   → http://localhost:8800/romih/
  • Telegram → @RomihAgentbot (polling)
  • API      → http://localhost:8800/romih/chat
"""
import sys, os, asyncio, threading, httpx, signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import RomihAgent, AgentConfig
from server.telegram_bot import TelegramBot, MessageHandler

# Config
PORT = int(os.environ.get("ROMIH_PORT", 8800))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8844618126:AAE-tPbM3__WNho1pTQp8SKEmaj5Gx--VxQ")
POLL_INTERVAL = 3

# ═══ FastAPI App ═══

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn

class ChatRequest(BaseModel):
    message: str
    task_type: str = "general"

app = FastAPI(title="Romih Agent")
agent = None
bot = None
handler = None

BASE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(BASE, "server")

# Serve static files
@app.get("/romih/")
async def serve_ui():
    path = os.path.join(SERVER, "ui.html")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return HTMLResponse(f.read(), media_type="text/html; charset=utf-8")
    return HTMLResponse("<h1>UI not found</h1>")

@app.get("/romih/dashboard")
async def serve_dashboard():
    path = os.path.join(SERVER, "dashboard.html")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return HTMLResponse(f.read(), media_type="text/html; charset=utf-8")
    return HTMLResponse("<h1>Dashboard not found</h1>")

@app.get("/romih/landing")
async def serve_landing():
    path = os.path.join(SERVER, "landing.html")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return HTMLResponse(f.read(), media_type="text/html; charset=utf-8")
    return HTMLResponse("<h1>Landing not found</h1>")

@app.get("/romih/health")
async def health():
    return {"status": "ok", "agent": "Romih Agent", "tools": len(agent.tools.tools) if agent else 0, "mode": "local"}

@app.get("/romih/status")
async def status():
    return agent.get_status() if agent else {}

@app.get("/romih/tools")
async def tools():
    if agent:
        cats = agent.tools.list_by_category()
        # Return only category names (hide tool names for security)
        safe = {cat: [t.get("name","?") for t in items] for cat, items in cats.items()}
        return {"categories": safe, "total": len(agent.tools.tools)}
    return {"categories": {}, "total": 0}

@app.get("/romih/memory")
async def memory():
    if agent and agent.memory:
        stats = agent.memory.long_term.get_stats()
        return {"total": stats.get("total", 0), "categories": stats.get("categories", {}), "last_updated": "active"}
    return {"total": 0, "categories": {}, "last_updated": "inactive"}

@app.post("/romih/chat")
async def chat(req: ChatRequest):
    response = await agent.chat(req.message, req.task_type)
    return {"response": response}

@app.post("/romih/goal")
async def goal(req: ChatRequest):
    response = await agent.execute_goal(req.message)
    return {"response": response}

# ═══ Telegram Bot ═══

async def run_telegram():
    """Poll Telegram in background"""
    print(f"Telegram: Connecting to @RomihAgentbot...")
    last_id = 0
    while True:
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.get(f"{bot.base}/getUpdates", params={
                    "offset": last_id + 1, "timeout": 5,
                    "allowed_updates": ["message", "callback_query"]
                })
                if r.status_code != 200:
                    await asyncio.sleep(POLL_INTERVAL)
                    continue
                
                data = r.json()
                if not data.get("ok"):
                    await asyncio.sleep(POLL_INTERVAL)
                    continue
                
                for update in data.get("result", []):
                    last_id = update["update_id"]
                    msg = bot.parse_message(update)
                    if msg and msg.get("text"):
                        print(f"[{msg.get('username','?')}] {msg['text'][:50]}")
                        await handler.handle(msg, bot)
        except Exception as e:
            print(f"Telegram poll: {e}")
        await asyncio.sleep(POLL_INTERVAL)

# ═══ Main ═══

async def main():
    global agent, bot, handler
    
    print("""
========================================
   Romih Agent v1.0 - Local Install
   Think. Plan. Execute. Repeat.
========================================""")
    
    # Init agent
    print("Initializing Romih Agent...")
    agent = RomihAgent(AgentConfig(
        name="Romih Admin",
        prefer_local=True,
        need_privacy=False
    ))
    status = agent.get_status()
    print(f"Tools: {status['tools_count']} | Loop: {status.get('agent_loop','?')} | Agents: {status['swarm_agents']}")
    
    # Init Telegram
    print("Starting Telegram bot...")
    bot = TelegramBot(TELEGRAM_TOKEN)
    handler = MessageHandler(agent)
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe")
            me = r.json().get("result", {})
            bot.me = me
        print(f"Bot: @{me.get('username', '?')} - connected")
    except:
        print("Telegram: not connected (skip)")
    
    # Start Telegram in background
    tg_task = asyncio.create_task(run_telegram())
    
    # Start web server
    print(f"""
========================================
  Web UI:   http://localhost:{PORT}/romih/
  Dashboard: http://localhost:{PORT}/romih/dashboard
  Landing:  http://localhost:{PORT}/romih/landing
  Telegram: @RomihAgentbot
========================================
Ready!
""")
    
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()
    
    tg_task.cancel()

def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nRomih Agent stopped.")

if __name__ == "__main__":
    run()
