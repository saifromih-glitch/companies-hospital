# -*- coding: utf-8 -*-
"""
Romih Agent - Local Runner
===========================
Runs Romih Agent locally on the user's machine.
Like AutoClaw - install once, ALL tools work.

Controlled via Telegram polling (no webhook needed).
"""
import sys, os, asyncio, httpx, signal

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import RomihAgent, AgentConfig
from server.telegram_bot import TelegramBot, MessageHandler

# Configuration
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8844618126:AAE-tPbM3__WNho1pTQp8SKEmaj5Gx--VxQ")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "sk-or-v1-f3b9bfaa52a02608c8e2b8a1b5f7e9d0c1a2b3c4d5e6f7a8b9c0d1e2f3a4b5")
POLL_INTERVAL = 3  # seconds between Telegram polls

class LocalRunner:
    """
    Local Runner - runs Romih Agent on the user's laptop.
    """
    
    def __init__(self):
        print("""
========================================
   Romih Agent - Local Runner v1.0
   74 tools - Think, Plan, Execute
========================================""")
        
        # Initialize agent with ALL tools
        print("Initializing Romih Agent...")
        self.agent = RomihAgent(AgentConfig(
            name="Mohammed Romih",
            prefer_local=True,
            need_privacy=False
        ))
        
        # Initialize Telegram bot
        print("Connecting to Telegram...")
        self.bot = TelegramBot(TELEGRAM_TOKEN)
        self.handler = MessageHandler(self.agent)
        
        self.running = False
        self.last_update_id = 0
    
    async def start(self):
        """Start the local runner"""
        # Verify Telegram connection
        try:
            self.bot.me = await self._get_me()
            print(f"Telegram: @{self.bot.me.get('username', 'unknown')} — connected")
        except Exception as e:
            print(f"Telegram error: {e}")
            print("Make sure TELEGRAM_BOT_TOKEN is set correctly")
            return
        
        # Show status
        status = self.agent.get_status()
        print(f"""
Configuration:
  Tools: {status['tools_count']}
  Sub-agents: {status['swarm_agents']}
  Agent Loop: {'Yes' if status['agent_loop'] else 'No'}
  Memory: {status['memory_items']} items
  Local models: {'Available' if status['prefer_local'] else 'Off'}
  Safety Shield: Active
  Secrets Vault: Active
  
Polling Telegram every {POLL_INTERVAL}s...
Ready! Send /start to @{self.bot.me.get('username', 'RomihAgentbot')}
============================================================
""")
        
        # Set commands
        await self.bot.set_commands()
        
        # Main polling loop
        self.running = True
        while self.running:
            try:
                await self._poll()
            except Exception as e:
                print(f"Poll error: {e}")
            await asyncio.sleep(POLL_INTERVAL)
    
    async def _poll(self):
        """Poll Telegram for new messages"""
        async with httpx.AsyncClient(timeout=15) as client:
            url = f"{self.bot.base}/getUpdates"
            params = {
                "offset": self.last_update_id + 1,
                "timeout": 5,
                "allowed_updates": ["message", "callback_query"]
            }
            r = await client.get(url, params=params)
            if r.status_code != 200:
                print(f"Telegram API error: {r.status_code}")
                return
            
            data = r.json()
            if not data.get("ok") or not data.get("result"):
                return
            
            for update in data["result"]:
                self.last_update_id = update["update_id"]
                
                # Handle callback queries
                if "callback_query" in update:
                    cq = update["callback_query"]
                    msg = cq.get("message", {})
                    data_text = cq.get("data", "")
                    await self._handle_update({
                        "message": {
                            "chat": msg.get("chat", {}),
                            "from": cq.get("from", {}),
                            "text": data_text
                        },
                        "callback_query": True
                    })
                    continue
                
                # Handle messages
                await self._handle_update(update)
    
    async def _handle_update(self, update: dict):
        """Handle a single update"""
        try:
            msg = self.bot.parse_message(update)
            if not msg or not msg.get("text"):
                return
            
            chat_id = msg["chat_id"]
            text = msg["text"].strip()
            
            print(f"\n[{msg.get('username', 'User')}] {text[:60]}")
            
            # Handle /goal with Agent Loop
            cmd, arg = self.bot.extract_command(text)
            if cmd == "/goal" and arg:
                await self.bot.send_chat_action(chat_id)
                await self.bot.send_message(chat_id, "Thinking... please wait")
                response = await self.agent.execute_goal(arg)
                await self.bot.send_message(chat_id, response)
                print(f"  → Goal executed ({len(response)} chars)")
                return
            
            # Handle via MessageHandler for other commands
            handled = await self.handler.handle(msg, self.bot)
            if not handled:
                # Fallback: normal chat
                await self.bot.send_chat_action(chat_id)
                response = await self.agent.chat(text)
                await self.bot.send_message(chat_id, response)
                print(f"  → Chat response ({len(response)} chars)")
                
        except Exception as e:
            print(f"  Handle error: {e}")
    
    async def _get_me(self) -> dict:
        """Get bot info"""
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe")
            return r.json().get("result", {})
    
    def stop(self):
        """Stop the runner"""
        self.running = False
        print("\nRomih Agent stopped.")


async def main():
    runner = LocalRunner()
    
    # Handle Ctrl+C
    def shutdown(sig, frame):
        print("\nShutting down...")
        runner.stop()
    
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    
    await runner.start()


if __name__ == "__main__":
    asyncio.run(main())
