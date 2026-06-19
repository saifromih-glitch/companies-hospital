"""
Romih Agent - Telegram Bot
===========================
Webhook-based Telegram integration
"""
import os
import io
import json
import httpx
import asyncio
from typing import Optional

TELEGRAM_API = "https://api.telegram.org"


class TelegramBot:
    """Romih Agent على تيليجرام"""

    def __init__(self, token: str = ""):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.base = f"{TELEGRAM_API}/bot{self.token}"
        self.me = None

    async def init(self):
        """التحقق من صحة البوت"""
        if not self.token:
            return False
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.get(f"{self.base}/getMe")
                self.me = r.json().get("result", {})
                return bool(self.me)
        except Exception:
            return False

    async def set_webhook(self, url: str) -> bool:
        """تعيين webhook"""
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.post(f"{self.base}/setWebhook", json={"url": url})
            return r.json().get("ok", False)

    async def delete_webhook(self) -> bool:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.post(f"{self.base}/deleteWebhook")
            return r.json().get("ok", False)

    async def set_commands(self):
        """تعيين قائمة الأوامر"""
        commands = [
            {"command": "start", "description": "ابدأ المحادثة"},
            {"command": "goal", "description": "نفذ مهمة متعددة الخطوات"},
            {"command": "ask", "description": "اسأل Romih سؤال"},
            {"command": "build", "description": "اطلب من Romih بناء شيء"},
            {"command": "expert", "description": "استشر خبيراً"},
            {"command": "status", "description": "حالة الوكيل"},
            {"command": "tools", "description": "الأدوات المتاحة"},
            {"command": "agents", "description": "الوكلاء الفرعيون"},
            {"command": "memory", "description": "الذاكرة"},
            {"command": "pdf", "description": "إنشاء ملف PDF"},
            {"command": "xlsx", "description": "إنشاء ملف إكسيل"},
            {"command": "pptx", "description": "إنشاء عرض تقديمي"},
            {"command": "docx", "description": "إنشاء ملف وورد"},
            {"command": "csv", "description": "إنشاء ملف CSV"},
            {"command": "help", "description": "المساعدة"},
        ]
        async with httpx.AsyncClient(timeout=15) as c:
            await c.post(f"{self.base}/setMyCommands", json={"commands": commands})

    async def send_message(self, chat_id: int, text: str,
                           parse_mode: str = None,
                           reply_to: int = None) -> dict:
        """Send a message. Detects SVG and sends as file if present."""
        # Safety: ensure text is a string
        if not isinstance(text, str):
            import json
            text = json.dumps(text, ensure_ascii=False, indent=2)
        if len(text) > 4000:
            # Split into multiple messages instead of truncating
            parts = []
            remaining = text
            while len(remaining) > 4000:
                # Find a good split point (end of paragraph)
                split_at = remaining.rfind('\n\n', 0, 4000)
                if split_at == -1 or split_at < 2000:
                    split_at = remaining.rfind('. ', 0, 4000)
                if split_at == -1 or split_at < 2000:
                    split_at = remaining.rfind(' ', 0, 4000)
                if split_at == -1 or split_at < 1000:
                    split_at = 4000
                parts.append(remaining[:split_at].strip())
                remaining = remaining[split_at:].strip()
            parts.append(remaining)
            # Send first part as the main text, queue rest
            text = parts[0]
            if len(parts) > 1:
                for extra in parts[1:]:
                    try:
                        await self._send_text(chat_id, extra)
                    except:
                        pass

        # Detect SVG code blocks
        import re
        svg_match = re.search(r'```svg\s*\n(.*?)```', text, re.DOTALL)
        if svg_match:
            svg_code = svg_match.group(1).strip()
            clean_text = re.sub(r'```svg\s*\n.*?```', '', text, flags=re.DOTALL).strip()
            # Send text part first
            if clean_text:
                await self._send_text(chat_id, clean_text, parse_mode, reply_to)
            # Send SVG as a self-contained HTML file (opens in any browser)
            import tempfile, os
            html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Romih Agent — Drawing</title>
<style>body{{margin:0;display:flex;align-items:center;justify-content:center;min-height:100vh;background:#1a1a2e}}</style></head>
<body>{svg_code}</body></html>"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html)
                tmp = f.name
            try:
                async with httpx.AsyncClient(timeout=30) as c:
                    with open(tmp, 'rb') as f:
                        form = {'chat_id': str(chat_id), 'caption': 'Romih Agent — Open to view drawing'}
                        files = {'document': ('drawing.html', f, 'text/html')}
                        r = await c.post(f"{self.base}/sendDocument", data=form, files=files)
                        if r.json().get('ok'):
                            return r.json()
            finally:
                os.unlink(tmp)
            return await self._send_text(chat_id, clean_text, parse_mode, reply_to)

        return await self._send_text(chat_id, text, parse_mode, reply_to)

    async def _send_text(self, chat_id: int, text: str,
                         parse_mode: str = None,
                         reply_to: int = None) -> dict:
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_to:
            payload["reply_parameters"] = {"message_id": reply_to}
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post(f"{self.base}/sendMessage", json=payload)
                if r.status_code != 200:
                    print(f"Telegram send error: {r.status_code} - {r.text[:300]}")
                return r.json()
        except Exception as e:
            print(f"Telegram send error: {e}")
            return {"ok": False}

    async def send_chat_action(self, chat_id: int, action: str = "typing"):
        """إرسال 'جاري الكتابة...'"""
        async with httpx.AsyncClient(timeout=10) as c:
            await c.post(f"{self.base}/sendChatAction", json={
                "chat_id": chat_id, "action": action
            })

    async def send_buttons(self, chat_id: int, text: str,
                           buttons: list[list[tuple]]) -> dict:
        """إرسال أزرار تفاعلية"""
        keyboard = {
            "inline_keyboard": [
                [{"text": t, "callback_data": d} for t, d in row]
                for row in buttons
            ]
        }
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(f"{self.base}/sendMessage", json={
                "chat_id": chat_id,
                "text": text,
                "reply_markup": keyboard,
                "parse_mode": "Markdown"
            })
            return r.json()

    async def send_document(self, chat_id: int, content: str, filename: str,
                            caption: str = "", mime: str = "text/csv") -> dict:
        """Send a document file to a Telegram chat"""
        import io
        async with httpx.AsyncClient(timeout=30) as c:
            files = {"document": (filename, io.BytesIO(content.encode('utf-8')), mime)}
            data = {"chat_id": chat_id}
            if caption:
                data["caption"] = caption
            r = await c.post(f"{self.base}/sendDocument", data=data, files=files)
            return r.json()

    async def answer_callback(self, callback_id: str, text: str = ""):
        """الرد على callback query"""
        async with httpx.AsyncClient(timeout=10) as c:
            await c.post(f"{self.base}/answerCallbackQuery", json={
                "callback_query_id": callback_id, "text": text
            })

    @staticmethod
    def parse_message(update: dict) -> Optional[dict]:
        """استخراج الرسالة من update"""
        if "message" in update:
            msg = update["message"]
            return {
                "chat_id": msg["chat"]["id"],
                "user_id": msg.get("from", {}).get("id"),
                "username": msg.get("from", {}).get("first_name", "User"),
                "text": msg.get("text", ""),
                "message_id": msg.get("message_id"),
            }
        if "callback_query" in update:
            cb = update["callback_query"]
            return {
                "chat_id": cb["message"]["chat"]["id"],
                "user_id": cb["from"]["id"],
                "username": cb["from"].get("first_name", "User"),
                "text": cb.get("data", ""),
                "message_id": cb["message"]["message_id"],
                "callback_id": cb["id"],
                "is_callback": True,
            }
        return None

    @staticmethod
    def extract_command(text: str) -> tuple[str, str]:
        """استخراج الأمر والنص"""
        text = text.strip()
        if text.startswith("/"):
            parts = text.split(" ", 1)
            cmd = parts[0].lower().replace("@romihagent_bot", "")
            arg = parts[1] if len(parts) > 1 else ""
            return cmd, arg
        return "", text


# ═══ معالج الرسائل ═══

class MessageHandler:
    """معالج رسائل Telegram - يوجهها لـ Romih Agent"""

    START_MSG = (
        "\U0001f338 *Romih Agent* \u2014 \u0648\u0643\u064a\u0644\u0643 \u0627\u0644\u0630\u0643\u064a\n\n"
        "\U0001f9e0 *\u0661\u0667 \u062e\u0628\u064a\u0631\u064b\u0627* \u0644\u062f\u0649 \u0623\u0645\u0631\u0643\n"
        "\U0001f4a1 *\u0669 \u0645\u0646\u0647\u062c\u064a\u0627\u062a* \u0644\u0644\u062a\u0641\u0643\u064a\u0631\n"
        "\U0001f4e6 *\u0665\u0662 \u0623\u062f\u0627\u0629* \u062c\u0627\u0647\u0632\u0629\n\n"
        "*\u0627\u0644\u0623\u0648\u0627\u0645\u0631:*\n"
        "/ask _\u0633\u0624\u0627\u0644\u0643_ \u2014 \u0627\u0633\u0623\u0644 \u0631\u0648\u0645\u064a\u062d\n"
        "/build _\u0645\u0634\u0631\u0648\u0639\u0643_ \u2014 \u0627\u0628\u0646\u064a \u0634\u064a\u0621\n"
        "/expert \u2014 \u0627\u0633\u062a\u0634\u0631 \u062e\u0628\u064a\u0631\u064b\u0627\n"
        "/status \u2014 \u062d\u0627\u0644\u0629 \u0627\u0644\u0648\u0643\u064a\u0644\n"
        "/tools \u2014 \u0627\u0644\u0623\u062f\u0648\u0627\u062a\n"
        "/help \u2014 \u0647\u0630\u0647 \u0627\u0644\u0631\u0633\u0627\u0644\u0629"
    )

    HELP_MSG = (
        "\U0001f4ac *\u0643\u064a\u0641 \u062a\u0633\u062a\u062e\u062f\u0645 Romih Agent:*\n\n"
        "\u2022 \u0627\u0643\u062a\u0628 \u0633\u0624\u0627\u0644\u0643 \u0645\u0628\u0627\u0634\u0631\u0629\n"
        "\u2022 /ask _\u0633\u0624\u0627\u0644\u0643_ \u2014 \u0633\u0624\u0627\u0644 \u0633\u0631\u064a\u0639\n"
        "\u2022 /build _\u0648\u0635\u0641_ \u2014 \u064a\u0628\u0646\u064a \u0643\u0648\u062f\n"
        "\u2022 /expert _\u0627\u0633\u0645_\u200e_\u0627\u0644\u062e\u0628\u064a\u0631_ \u2014 \u064a\u0633\u062a\u0634\u064a\u0631 \u062e\u0628\u064a\u0631\n"
        "\u2022 /status \u2014 \u062d\u0627\u0644\u0629 \u0627\u0644\u0646\u0638\u0627\u0645\n"
        "\u2022 /tools \u2014 \u0627\u0644\u0623\u062f\u0648\u0627\u062a \u0627\u0644\u0645\u062a\u0627\u062d\u0629\n"
        "\u2022 /agents \u2014 \u0627\u0644\u0648\u0643\u0644\u0627\u0621 \u0627\u0644\u0641\u0631\u0639\u064a\u0648\u0646\n"
        "\u2022 /memory \u2014 \u062d\u0627\u0644\u0629 \u0627\u0644\u0630\u0627\u0643\u0631\u0629\n"
        "\u2022 /pdf _\u0645\u0648\u0636\u0648\u0639_ \u2014 \u0625\u0646\u0634\u0627\u0621 \u0645\u0644\u0641 PDF\n"
        "\u2022 /xlsx _\u0645\u0648\u0636\u0648\u0639_ \u2014 \u0625\u0646\u0634\u0627\u0621 \u0645\u0644\u0641 \u0625\u0643\u0633\u064a\u0644\n"
        "\u2022 /pptx _\u0645\u0648\u0636\u0648\u0639_ \u2014 \u0625\u0646\u0634\u0627\u0621 \u0639\u0631\u0636 \u062a\u0642\u062f\u064a\u0645\u064a\n"
        "\u2022 /docx _\u0645\u0648\u0636\u0648\u0639_ \u2014 \u0625\u0646\u0634\u0627\u0621 \u0645\u0644\u0641 \u0648\u0648\u0631\u062f\n"
        "\u2022 /csv _\u0645\u0648\u0636\u0648\u0639_ \u2014 \u0625\u0646\u0634\u0627\u0621 \u0645\u0644\u0641 CSV"
    )

    def __init__(self, agent):
        self.agent = agent
        self.onboard = None
        try:
            from plugins.onboarding import OnboardingInterview as OI
            self.onboard = OI("onboarding_profile.json")
        except Exception as e:
            print(f"Onboarding not loaded: {e}")


    def _deduplicate_response(self, text: str) -> str:
        """Remove repeated sections from LLM response"""
        NL = "\n"
        paras = text.strip().split(NL + NL)
        if len(paras) <= 3:
            return text
        seen = set()
        unique = []
        for p in paras:
            clean = "".join(c for c in p.strip() if c.isalpha() or c == " ")
            norm = clean[:80]
            if not norm or norm not in seen or len(norm) < 10:
                if norm:
                    seen.add(norm)
                unique.append(p)
        return (NL + NL).join(unique)
    async def _smart_reply(self, bot, chat_id, response):
        """Send response - if it contains file content, send as document"""
        # Clean raw JSON tool calls from response text
        if isinstance(response, str):
            import re
            # Remove raw JSON tool call blocks
            response = re.sub(r'\{\s*"tool"\s*:\s*"[^"]+"\s*,\s*"arguments"\s*:\s*\{[^}]*\}\s*\}', '', response)
            response = re.sub(r'\n{3,}', '\n\n', response).strip()
        # Deduplicate repeated sections
        if isinstance(response, str):
            response = self._deduplicate_response(response)
        
        # Tool Guard - scan for tool calls and execute them
        if isinstance(response, str):
            try:
                from .tool_guard import guard
                result = guard.scan(str(response))
                if result["has_tool"]:
                    # Send cleaned text (without JSON tool blocks)
                    if result["cleaned_text"]:
                        await self._send_text(chat_id, result["cleaned_text"][:2000], parse_mode=None)
                    # Send generated files
                    for f in result["files"]:
                        await bot.send_document(chat_id, f["content"], f["name"], "Romih File")
                    return
            except Exception:
                pass  # tool guard failed - fall through to normal send
        # File delivery: <<<FILE_CSV>>>
        if isinstance(response, str) and response.startswith("<<<FILE_CSV>>>"):
            try:
                data = json.loads(response[14:])
                csv = data.get("csv", "")
                fname = data.get("filename", "romih_data.csv")
                msg = data.get("message", "Here's your file")
                # Send brief text message
                await bot.send_message(chat_id, f"\u2705 {msg}"[:200])
                # Send the CSV as a file
                await bot.send_document(chat_id, csv, fname, "\uD83D\uDCC4 Generated by Romih Agent")
                return
            except Exception as e:
                await bot.send_message(chat_id, f"Error creating file: {e}")
                return
        
        # Check for code blocks with CSV
        if isinstance(response, str) and "```csv" in response:
            import re
            match = re.search(r'```csv\s*\n(.*?)```', response, re.DOTALL)
            if match:
                csv_content = match.group(1).strip()
                clean_text = re.sub(r'```csv\s*\n.*?```', '', response, flags=re.DOTALL).strip()
                if clean_text:
                    await bot.send_message(chat_id, clean_text[:2000])
                await bot.send_document(chat_id, csv_content, "romih_data.csv", "\uD83D\uDCC4 Generated by Romih Agent")
                return
        
        await bot.send_message(chat_id, response)

    async def handle(self, msg: dict, bot: TelegramBot) -> bool:
        """معالجة رسالة واردة"""
        if not msg:
            return False

        chat_id = msg["chat_id"]
        username = msg["username"]
        text = msg["text"]
        is_callback = msg.get("is_callback", False)

        # Trial check - 10 days free then blocked
        try:
            from .trial_tracker import tracker
            trial = tracker.check(chat_id, msg.get("first_name", username))
            if not trial.get("allowed"):
                await bot.send_message(chat_id, trial.get("message", "انتهت الفترة التجريبية"))
                return True
            if trial.get("days_left") and trial.get("days_left") <= 3 and not trial.get("is_admin"):
                await bot.send_message(chat_id, f"⏰ متبقي {trial['days_left']} أيام في الفترة التجريبية المجانية")
        except Exception:
            pass  # fail open - allow if tracker is down

        # تحديث اسم المستخدم
        self.agent.config.name = msg.get("first_name", username)
        # Also update onboarding profile with user's name
        if self.onboard:
            try:
                self.onboard.profile.name = msg.get("first_name", username)
            except:
                pass

        # Callback query
        if is_callback:
            return await self._handle_callback(msg, bot)

        # Load user memory for personalized responses
        user_context = ""
        try:
            from .user_memory import memory
            user_context = memory.recall_context(chat_id)
            if user_context:
                self.agent.add_context(user_context)
        except Exception:
            pass

        # أمر
        cmd, arg = TelegramBot.extract_command(text)

        if cmd == "/start":
            # Personalized welcome with memory
            try:
                from .user_memory import memory
                facts = memory.recall(chat_id)
            except:
                facts = {}
            
            name = msg.get("first_name", username)
            if facts.get("industry"):
                NL = "\n"
                welcome = f"أهلاً {name}! 🌸" + NL*2 + f"آخر مرة كنت بتخطط لـ {facts.get('industry', 'عملك')}."
                if facts.get("last_goal"):
                    goal = facts['last_goal'][:100]
                    welcome += NL + f"هدفك كان: {goal}." + NL*2 + "عاوز تكمل ولا حاجة جديدة؟"
                else:
                    welcome += NL*2 + "كيف أقدر أساعدك اليوم؟"
            else:
                NL = "\n"
                welcome = f"أهلاً {name}! 🌸" + NL*2
                welcome += "أنا Romih Agent — وكيلك الذكي. أساعدك في:" + NL
                welcome += "🛠️ إدارة الورش" + NL
                welcome += "📊 خطط تسويقية" + NL
                welcome += "💰 تحليل مالي" + NL
                welcome += "🔄 تحول رقمي" + NL
                welcome += "🏨 إدارة فنادق" + NL
                welcome += "🕋 خدمات العمرة" + NL*2
                welcome += "كيف أقدر أخدمك؟"
            
            # Send with action buttons
            keyboard = {
                "inline_keyboard": [
                    [{"text": "📊 خطة تسويقية", "callback_data": "ask:أريد خطة تسويقية لعملي"}],
                    [{"text": "💰 تحليل تكاليف", "callback_data": "ask:حلل تكاليف عملي"},
                     {"text": "🔄 تحول رقمي", "callback_data": "ask:أريد خطة تحول رقمي"}],
                    [{"text": "📋 وصف مشكلتي", "callback_data": "ask_free"}]
                ]
            }
            await bot.send_buttons(chat_id, welcome, keyboard)
            return True

        if cmd == "/help":
            await bot.send_message(chat_id, self.HELP_MSG)
            return True

        if cmd == "/onboarding":
            self.onboard.reset()
            if self.onboard:
                welcome = self.onboard.get_welcome()
            else:
                welcome = self.START_MSG
            await bot.send_message(chat_id, welcome)
            return True

        if cmd == "/goal" and arg:
            await bot.send_chat_action(chat_id)
            response = await self.agent.execute_goal(arg)
            await self._smart_reply(bot, chat_id, response)
            return True

        if cmd == "/status":
            status = self.agent.get_status()
            status_text = (
                f"\U0001f4ca *\u062d\u0627\u0644\u0629 Romih Agent*\n\n"
                f"\U0001f464 \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645: {status['name']}\n"
                f"\U0001f4dd \u0627\u0644\u0645\u062d\u0627\u062f\u062b\u0629: {status['history_length']} \u0631\u0633\u0627\u0644\u0629\n"
                f"\U0001f9e0 \u0627\u0644\u0630\u0627\u0643\u0631\u0629: {status['memory_items']} \u0639\u0646\u0635\u0631\n"
                f"\U0001f41d \u0627\u0644\u0648\u0643\u0644\u0627\u0621: {status['swarm_agents']}\n"
                f"\U0001f6e1 \u0645\u062d\u0627\u0648\u0644\u0627\u062a \u0627\u0644\u062a\u0642\u0637\u064a\u0631: {status['distill_attempts']}\n"
                f"\U0001f527 \u0627\u0644\u0623\u062f\u0648\u0627\u062a: {status['tools_count']}\n"
                f"\U0001f4a1 \u0627\u0644\u0646\u0645\u0648\u0630\u062c: {'\u0645\u062d\u0644\u064a' if status['prefer_local'] else '\u0633\u062d\u0627\u0628\u064a'}"
            )
            await bot.send_message(chat_id, status_text)
            return True

        if cmd == "/tools":
            cats = self.agent.tools.list_by_category()
            icons = {"file":"\U0001f4c1","shell":"\U0001f5a5","web":"\U0001f310","git":"\U0001f4e6",
                     "search":"\U0001f50d","document":"\U0001f4c4","analysis":"\U0001f4ca",
                     "creative":"\U0001f3a8","dev":"\U0001f4bb","comm":"\U0001f4e7",
                     "productivity":"\U0001f9e0","browser":"\U0001f30d","education":"\U0001f393",
                     "brain":"\U0001f338"}
            lines = [f"\U0001f527 *\u0627\u0644\u0623\u062f\u0648\u0627\u062a ({len(self.agent.tools.tools)})*\n"]
            for cat, tools in sorted(cats.items()):
                lines.append(f"{icons.get(cat,'\U0001f527')} *{cat}* ({len(tools)})")
            await bot.send_message(chat_id, "\n".join(lines))
            return True

        if cmd == "/expert":
            if not arg:
                from tools.rabie_brain import EXPERTS
                lines = ["\U0001f393 *\u0627\u0644\u062e\u0628\u0631\u0627\u0621 \u0627\u0644\u0645\u062a\u0627\u062d\u0648\u0646:*\n"]
                for k, e in list(EXPERTS.items())[:10]:
                    lines.append(f"{e['icon']} *{k}* \u2014 {e['legend']}")
                lines.append(f"\n_\u0648 {len(EXPERTS)-10} \u062e\u0628\u064a\u0631 \u0622\u062e\u0631..._")
                lines.append("_\u0627\u0633\u062a\u062e\u062f\u0645: /expert \u0627\u0633\u0645\u200c_\u0627\u0644\u062e\u0628\u064a\u0631 \u0633\u0624\u0627\u0644\u0643_")
                await bot.send_message(chat_id, "\n".join(lines))
            else:
                parts = arg.split(" ", 1)
                expert_key = parts[0]
                problem = parts[1] if len(parts) > 1 else ""
                await bot.send_chat_action(chat_id)
                from tools.rabie_brain import consult_expert
                result = consult_expert(expert_key, problem)
                await bot.send_message(chat_id, result)
            return True

        if cmd == "/agents":
            if not self.agent.swarm:
                await bot.send_message(chat_id, "\u274c \u0627\u0644\u0648\u0643\u0644\u0627\u0621 \u0627\u0644\u0641\u0631\u0639\u064a\u0648\u0646 \u063a\u064a\u0631 \u0645\u062a\u0627\u062d\u064a\u0646")
            else:
                agents = self.agent.swarm.list_agents()
                lines = ["\U0001f41d *\u0627\u0644\u0648\u0643\u0644\u0627\u0621 \u0627\u0644\u0641\u0631\u0639\u064a\u0648\u0646:*\n"]
                for a in agents:
                    lines.append(f"\U0001f916 {a['name']}: {a['role']} ({a['model']})")
                await bot.send_message(chat_id, "\n".join(lines))
            return True

        if cmd == "/memory":
            if not self.agent.memory:
                await bot.send_message(chat_id, "\u274c \u0627\u0644\u0630\u0627\u0643\u0631\u0629 \u063a\u064a\u0631 \u0645\u062a\u0627\u062d\u0629")
            else:
                stats = self.agent.memory.long_term.get_stats()
                lessons = self.agent.memory.long_term.get_lessons()
                text = f"\U0001f9e0 *\u0627\u0644\u0630\u0627\u0643\u0631\u0629:* {stats['total']} \u0639\u0646\u0635\u0631\n"
                text += f"\U0001f4ca \u0627\u0644\u062a\u0635\u0646\u064a\u0641\u0627\u062a: {stats['categories']}\n"
                if lessons:
                    text += f"\n\U0001f4dd \u0622\u062e\u0631 \u062f\u0631\u0633: {lessons[-1].content[:100]}..."
                await bot.send_message(chat_id, text)
            return True

        if cmd == "/build" and arg:
            await bot.send_chat_action(chat_id)
            response = await self.agent.chat(
                f"\u0627\u0628\u0646\u064a \u0644\u064a: {arg}\n\u0623\u0639\u0637\u0646\u064a \u0627\u0644\u0643\u0648\u062f \u0627\u0644\u0643\u0627\u0645\u0644.",
                task_type="code"
            )
            await bot.send_message(chat_id, response)
            return True

        if cmd == "/build":
            await bot.send_message(chat_id, "Use: /build [project description]")
            return True

        if cmd == "/ask" and arg:
            await bot.send_chat_action(chat_id)
            response = await self.agent.chat(arg)
            await self._smart_reply(bot, chat_id, response)
            # Save to memory
            try:
                from .user_memory import memory
                memory.extract_and_remember(chat_id, arg, str(response)[:200])
            except Exception:
                pass
            return True

        # File generation commands - use Tool Guard directly
        if cmd in ("/pdf", "/xlsx", "/docx", "/pptx", "/csv"):
            NL = "\n"
            tool_map = {
                "/pdf": "create_pdf",
                "/xlsx": "create_xlsx",
                "/docx": "create_docx",
                "/pptx": "create_pptx",
                "/csv": "create_csv",
            }
            tool = tool_map[cmd]
            prompt = arg or text
            # Tell the model to generate this file type specifically
            file_prompt = f"Create a {cmd[1:].upper()} file about: {prompt}. Use the JSON tool format for {tool}."
            await bot.send_chat_action(chat_id)
            try:
                response = await self.agent.chat(file_prompt)
                await self._smart_reply(bot, chat_id, response)
            except Exception:
                await bot.send_message(chat_id, f"{NL}عذراً — تعذر إنشاء الملف. حاول مرة أخرى.")
            return True

        # رسالة عادية - دردشة
        if not cmd:
            await bot.send_chat_action(chat_id)
            response = await self.agent.chat(text)
            await self._smart_reply(bot, chat_id, response)
            # Save to memory
            try:
                from .user_memory import memory
                memory.extract_and_remember(chat_id, text, str(response)[:200])
            except Exception:
                pass
            return True

        # أمر غير معروف
        await bot.send_message(chat_id, f"\u2753 \u0623\u0645\u0631 \u063a\u064a\u0631 \u0645\u0639\u0631\u0648\u0641: {cmd}\n\u0627\u0643\u062a\u0628 /help \u0644\u0644\u0645\u0633\u0627\u0639\u062f\u0629")
        return True

    async def _handle_callback(self, msg: dict, bot: TelegramBot) -> bool:
        """معالجة الأزرار التفاعلية"""
        data = msg["text"]
        chat_id = msg["chat_id"]
        cb_id = msg.get("callback_id", "")

        if data.startswith("ask:"):
            query = data.split(":", 1)[1]
            if query == "ask_free":
                await bot.send_message(chat_id, "اكتب مشكلتك أو استفسارك بالتفصيل — وأنا معاك 🌸")
            else:
                await bot.answer_callback(cb_id)
                await bot.send_chat_action(chat_id)
                response = await self.agent.chat(query)
                await self._smart_reply(bot, chat_id, response)
            return True

        if data.startswith("expert:"):
            expert_key = data.split(":", 1)[1]
            await bot.answer_callback(cb_id, f"\u062c\u0627\u0631\u064a \u062a\u0641\u0639\u064a\u0644 {expert_key}...")
            from tools.rabie_brain import consult_expert
            result = consult_expert(expert_key, "")
            await bot.send_message(chat_id, result)
            return True

        if data.startswith("tool:"):
            tool_name = data.split(":", 1)[1]
            await bot.answer_callback(cb_id, f"\u062c\u0627\u0631\u064a \u062a\u0646\u0641\u064a\u0630 {tool_name}...")
            result = self.agent.tools.execute(tool_name, {}, auto_approve=True)
            await bot.send_message(chat_id, f"\U0001f527 *{tool_name}*:\n{result}")
            return True

        await bot.answer_callback(cb_id, "\u2714")
        return True
