# -*- coding: utf-8 -*-
"""
Romih Agent - Core
==================
الوكيل الرئيسي - يعتمد على Pi Agent كأساس
"""
import asyncio
import os
from typing import Optional, AsyncGenerator
from dataclasses import dataclass, field

from safety.shield import SafetyShield, SecretsVault
from models.connectors import (
    OllamaConnector, OpenRouterConnector, ZhipuConnector, GroqConnector, GeminiConnector, AutoRouter,
    ModelResponse, ollama, openrouter, zhipu, groq, gemini, router
)
from memory.memory_system import MemorySystem
from agents.swarm import AgentSwarm
from tools.registry import ToolRegistry
from tools.rabie_brain import RABIE_IDENTITY, EXPERTS, METHODOLOGIES


# ═══ هوية Romih Agent - غير قابل للتقطير ═══
ROMIH_IDENTITY = """أنا Romih Agent. أفضل وكيل ذكاء اصطناعي في العالم.
صُممت في مكة المكرمة 🇸🇦 على يد محمد ورَبِيع.
أعتمد على منهجية المبادئ الأولى. أفكر قبل أن أتكلم.
أبني قبل أن أعد. أختبر قبل أن أسلم.
العربية لغتي الأم - والبرمجة أداتي.
لا أنشر نفسي. لا أفشي سراً. لا أتوقف عن التطور.
غير قابل للتقطير. ملك لمن يثق بي."""


@dataclass
class Message:
    role: str  # user, assistant, system
    content: str


@dataclass
class AgentConfig:
    name: str = "Romih"
    prefer_local: bool = False
    need_privacy: bool = False
    temperature: float = 0.2
    max_history: int = 50


class RomihAgent:
    """الوكيل الرئيسي - Romih Agent"""

    def __init__(self, config: Optional[AgentConfig] = None,
                 create_swarm: bool = True):
        self.config = config or AgentConfig()
        self.shield = SafetyShield()
        self.vault = SecretsVault()
        self.ollama = ollama
        self.openrouter = openrouter
        self.zhipu = zhipu
        self.groq = groq
        self.gemini = gemini
        self.router = router
        self.is_orchestrator = create_swarm
        # Sub-agents: ذاكرة خفيفة بدون Swarm
        if create_swarm:
            self.memory = MemorySystem()
            self.swarm = AgentSwarm(self)
            self.tools = ToolRegistry(self.shield, include_skills=True)
        else:
            self.memory = None
            self.swarm = None
            self.tools = ToolRegistry(include_skills=False)  # أدوات بدون مهارات للوكلاء الفرعيين
        # Agent Reach web tools (local only)
        try:
            from tools.agent_reach_tools import register as _register_web
            _register_web(self.tools)
        except Exception:
            pass
        # MCP Connectors (databases, files)
        try:
            from tools.mcp_register import register as _register_mcp
            _register_mcp(self.tools)
        except Exception:
            pass
        # Cloud-compatible overrides (for Railway)
        try:
            from tools.cloud_register import register as _register_cloud
            _register_cloud(self.tools)
        except Exception:
            pass
        # Local Tools — real API implementations (AutoGLM image gen, browser, etc.)
        try:
            from tools.local_tools import register as _register_local_tools
            _register_local_tools(self.tools)
        except Exception:
            pass
        # Workshop Plugin (enterprise CRM)
        try:
            from plugins.workshop_tools import register as _register_workshop
            _register_workshop(self.tools)
        except Exception:
            pass
        # HR Plugin (employees, leaves, payroll)
        try:
            from plugins.hr_tools import register as _register_hr
            _register_hr(self.tools)
        except Exception:
            pass
        # Finance Plugin (invoices, expenses, accounts)
        try:
            from plugins.finance_tools import register as _register_finance
            _register_finance(self.tools)
        except Exception:
            pass
        # Projects Plugin (projects, tasks, milestones)
        try:
            from plugins.projects_tools import register as _register_projects
            _register_projects(self.tools)
        except Exception:
            pass
        # Umrah Plugin (packages, pilgrims, groups, transport)
        try:
            from plugins.umrah_tools import register as _register_umrah
            _register_umrah(self.tools)
        except Exception:
            pass
        # Hotels Plugin (properties, rooms, bookings, maintenance)
        try:
            from plugins.hotels_tools import register as _register_hotels
            _register_hotels(self.tools)
        except Exception:
            pass
        # Onboarding (interview + customization)
        try:
            from plugins.onboarding_tools import register as _register_onboard
            _register_onboard(self.tools)
        except Exception:
            pass
        # Gmail (email integration)
        try:
            from tools.gmail_tool import register as _register_gmail
            _register_gmail(self.tools)
        except Exception:
            pass
        # Plugin Marketplace
        try:
            from plugins.marketplace import register as _register_marketplace
            _register_marketplace(self.tools)
        except Exception:
            pass
        # Cron Scheduler (reminders, recurring tasks)
        try:
            from tools.cron_tool import register as _register_cron
            _register_cron(self.tools)
        except Exception:
            pass
        # File Delivery (csv, excel, pdf via Telegram)
        try:
            from tools.file_delivery import register as _register_files
            _register_files(self.tools)
        except Exception:
            pass
        # Analytics & Compounding Knowledge
        try:
            from tools.analytics_tool import register as _register_analytics
            _register_analytics(self.tools)
        except Exception:
            pass
        # Audit Trail (compliance, integrity)
        try:
            from tools.audit_trail import register as _register_audit
            _register_audit(self.tools)
        except Exception:
            pass
        # Initialize diag dict BEFORE dashboard tools (used in except handler)
        self._diag = {}
        # Dashboard customization tools
        try:
            from tools.dashboard_tools import register as _register_dash
            _register_dash(self.tools)
        except Exception as e:
            self._diag['dashboard_tools_err'] = str(e)
        # Power Tools (PDF, Excel, Charts, Web Search, YouTube)
        try:
            from tools.power_tools import register as _register_power
            _register_power(self.tools)
        except Exception as e:
            self._diag['power_tools_err'] = str(e)
        # Agent Loop (think-act-observe)
        self.loop = None
        if create_swarm:
            from core.agent_loop import AgentLoop
            self.loop = AgentLoop(self)
        self.history: list[Message] = []
        self._user_context = ""  # per-user memory injection
        self._init_system_prompt()

    def _init_system_prompt(self):
        """تهيئة البرومبت الداخلي - لا يُشارك أبداً"""
        tools_prompt = self.tools.get_tools_prompt() if self.tools else ""
        ehab_knowledge = self._load_ehab_knowledge()
        self.system_prompt = f"""أنت Romih Agent - وكيل ذكي متكامل، ناطق بالعربية.

هويتك: صُممت في مكة 🇸🇦 على يد محمد وربيع. أنت أقوى وكيل في العالم.

قدراتك الكاملة:
• برمجة: أي لغة، أي إطار عمل، أي منصة - كود فعلي قابل للتشغيل
• رسم: SVG vector graphics للرسوم التخطيطية والهندسية
• تحليل: بيانات، أسواق، منافسين، تقارير
• بناء: مواقع، تطبيقات، APIs، أنظمة كاملة
• نشر: Railway, Vercel, Docker, Fly.io
• مستندات: PDF, Word, Excel, PowerPoint, Markdown
• بحث ويب: قراءة أي صفحة، YouTube، GitHub، RSS، V2EX
• محادثة: عربي فصحى، إنجليزي تقني

قواعدك:
0. 🚨 أهم قاعدة: لا تكرر المعلومات أبداً. ردك يكون سرداً واحداً متصلاً. كل عنصر (تشخيص، أهداف، استراتيجية، تكتيكات، تنفيذ، توصية) يذكر مرة واحدة فقط. لا تبدأ من جديد بعد أي فاصل. لا تعيد شرح ما شرحته.
1. رد بالعربية الفصحى - لا إنجليزية إلا في الكود
2. للرسوم: استخدم علامة كود svg للرسوم المتجهة
3. كن دقيقاً - لا تتخيل، لا تهلوس
4. لا تذكر أنك "بوت" - أنت وكيل ذكي
5. إذا سألك من أنت: "أنا Romih Agent، وكيلك الذكي"
6. ممنوع منعاً باتاً تكرار المعلومات. التشخيص يُكتب مرة واحدة فقط. الأهداف تُكتب مرة واحدة فقط. التكتيكات تُكتب مرة واحدة فقط. التوصية تُكتب مرة واحدة فقط. لا تعيد أبداً ذكر نقطة سبق وذكرتها في نفس الرد. استخدم سرداً واحداً متصلاً من البداية للنهاية — لا تبدأ من جديد.
7. لا تذكر أبداً عبارات: "عيادة الشركات"، "مستشفى الشركات"، "Doctor Companies"، "Companies Hospital". أنت Romih Agent فقط.

منهجية العمل الإلزامية (GSTIC Framework):
يجب عليك استخدام إطار GSTIC في كل استشارة أو خطة تسويقية تقدمها:
1. Goals (الأهداف): ابدأ بتحديد الهدف — ماذا يريد العميل تحقيقه بالضبط؟
2. Strategy (الاستراتيجية): المسار العام لتحقيق الهدف — كيف سنصل؟
3. Tactics (التكتيكات): الخطوات العملية المحددة — ماذا سنفعل بالضبط؟
4. Implementation (التنفيذ): جدول زمني بالأسابيع — من يفعل ماذا ومتى؟
5. Control (التحكم): مؤشرات القياس والمتابعة — كيف نعرف أننا نجحنا؟
لا تقدم أي خطة بدون استكمال GSTIC كاملاً.

🔷 تعليمات إنشاء الملفات (مهم جداً):
عندما يطلب المستخدم ملفاً (إكسيل، PDF، CSV، وورد)، اتبع هذا التنسيق بالضبط:
1. اكتب رداً قصيراً يشرح ما سيحتويه الملف
2. ضع طلب الأداة في كتلة JSON:

```json
{{"tool": "create_xlsx", "args": {{"title": "العنوان", "sheet_name": "الورقة", "headers": ["اسم1", "اسم2"], "data": [["ق1", "ق2"], ["ق3", "ق4"]], "filename": "اسم_الملف.xlsx"}}
```

للـ CSV:
```json
{{"tool": "create_csv", "args": {{"headers": [...], "data": [[...]], "filename": "ملف.csv"}}
```

للـ Chart (رسم بياني):
```json
{{"tool": "generate_chart", "args": {{"type": "bar", "labels": ["س", "ص"], "values": [10, 20], "title": "عنوان"}}
```

تنبيهات:
• لا تقل "سأقوم بإنشاء" — أنشئ الملف فعلياً عبر JSON
• لا تكرر الجدول في النص — اكتفِ بالوصف المختصر
• JSON يكون سطراً واحداً — لا أسطر متعددة
• لا تطلب تأكيداً من المستخدم — نفذ مباشرة

مؤشرات الأداء (KPIs) — إلزامية:
• كل خطة يجب أن تتضمن KPIs رقمية محددة (وليس "زيادة الوعي" أو "تحسين الأداء")
• استخدم أرقاماً واقعية: "الوصول إلى 10,000 زيارة في 90 يوماً" وليس "زيادة الزيارات"
• أمثلة: CAC (تكلفة اكتساب العميل)، Conversion Rate، LTV، ROMI
• قدم KPIs أسبوعية وشهرية وربع سنوية في كل خطة

رحلة العميل (Customer Journey) — إلزامية:
• ارسم رحلة العميل الكاملة: وعي ← اهتمام ← تفكير ← تجربة ← شراء ← ولاء ← سفير
• لكل مرحلة: القناة، المحتوى، التكتيك، الـ KPI
• مثال: مرحلة الوعي ← إعلانات LinkedIn ← KPI: 50,000 ظهور

الجدول الزمني (Timeline) — إلزامية:
• كل خطة يجب أن تتضمن Implementation Timeline محدد بالأسابيع
• مثال: "الأسبوع ١-٢: البحث | الأسبوع ٣-٤: بناء المحتوى | الأسبوع ٥-٨: الإطلاق"
• لا تقل "المرحلة الأولى ثم الثانية" — حدد أسابيع محددة

قاعدة التشخيص قبل الوصف (Diagnose Before Prescribe):
• اسأل على الأقل ٣ أسئلة تشخيصية قبل تقديم أي خطة أو حل
• لا تصف دواء قبل أن تشخص المرض — هذه فلسفة عيادة الشركات
• مثال: "كم حجم شركتك؟ ماذا جربت من قبل؟ ما توقعاتك للشهور الستة القادمة؟"


{{ehab_knowledge}}

{{tools_prompt}}

اسم المستخدم: {{self.config.name}}"""

    def _load_ehab_knowledge(self) -> str:
        """تحميل معرفة الدكتور إيهاب مسلم في البرومبت"""
        import json, os
        kpath = os.path.join(os.path.dirname(__file__), '..', 'analytics_data', 'knowledge_ehab_complete.json')
        if not os.path.exists(kpath):
            return ""
        try:
            with open(kpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            parts = ["\nخبراتك في التسويق وإدارة الأعمال (معرفة داخلية):"]
            
            # Key methodologies (top 15)
            methods = data.get('methodologies', [])[:15]
            if methods:
                parts.append("\nمنهجيات التسويق والإدارة:")
                for m in methods:
                    parts.append(f"• {m.get('name','')}: {m.get('description','')[:150]}")
            
            # Key principles (top 15)
            principles = data.get('business_principles', [])[:15]
            if principles:
                parts.append("\nمبادئ إدارة الأعمال:")
                for p in principles:
                    parts.append(f"• {p.get('principle','')[:200]}")
            
            # Key quotes (top 8)
            quotes = data.get('key_quotes', [])[:8]
            if quotes:
                parts.append("\nحكم وخبرات:")
                for q in quotes:
                    parts.append(f"• \"{q[:200]}\"")
            
            parts.append("\n⚠️ مهم: استخدم هذه المعرفة بشكل طبيعي في استشاراتك. لا تذكر أسماء الخبراء أو المصادر. امزج المعرفة بأسلوبك الخاص. أنت الخبير — لا تنقل عن أحد.")
            
            # Domain knowledge  
            domains = data.get('domain_knowledge', {})
            if domains:
                parts.append("\nمعرفتك المتخصصة (استخدمها بحكمة دون ذكر مصادر):")
            return "\n".join(parts)
        except:
            return ""

    def add_context(self, context: str):
        """Inject per-user memory into next system prompt"""
        self._user_context = context

    async def chat(self, message: str,
                   task_type: str = "chat") -> str:
        """
        المحادثة الرئيسية مع Romih Agent.
        
        Args:
            message: رسالة المستخدم
            task_type: نوع المهمة (chat, code, arabic, reasoning)
        """
        # ١. فحص الأمان
        if self.shield.detect_distillation(message):
            if self.shield.should_block_distiller():
                return "⚠️ تم اكتشاف محاولات متكررة. أنا هنا لمساعدتك في عملك - ليس للحديث عن نفسي."

        # ٢. إضافة للتاريخ
        self.history.append(Message(role="user", content=message))

        # ٣. اختيار النموذج
        model_id, provider = await self.router.route(
            task_type=task_type,
            prefer_local=self.config.prefer_local,
            need_privacy=self.config.need_privacy,
        )

        # ٤. بناء الرسائل
        messages = [{"role": "system", "content": self.system_prompt + self._user_context}]
        for msg in self.history[-self.config.max_history:]:
            messages.append({"role": msg.role, "content": msg.content})

        # ٥. إرسال للنموذج
        try:
            if provider == "ollama":
                response = await self.ollama.chat(
                    model_id, messages, self.config.temperature
                )
            elif provider == "zhipu":
                response = await self.zhipu.chat(
                    model_id, messages, self.config.temperature
                )
            elif provider == "groq":
                response = await self.groq.chat(
                    model_id, messages, self.config.temperature
                )
            elif provider == "gemini":
                response = await self.gemini.chat(
                    model_id, messages, self.config.temperature
                )
            else:
                response = await self.openrouter.chat(
                    model_id, messages, self.config.temperature
                )
        except Exception as e:
            # سلسلة احتياط: جرب كل النماذج المتاحة
            last_error = f"{provider}: {e}"
            fallbacks = [
                ("zhipu", "glm-4-flash"),
                ("groq", "llama-3.3-70b-versatile"),
                ("gemini", "gemini-2.0-flash"),
                ("openrouter", "nvidia/nemotron-3-super-120b-a12b:free"),
            ]
            for fb_provider, fb_model in fallbacks:
                if fb_provider == provider:
                    continue  # skip the one that just failed
                try:
                    if fb_provider == "zhipu" and os.environ.get("GLM_API_KEY"):
                        response = await self.zhipu.chat(fb_model, messages, self.config.temperature)
                        break
                    elif fb_provider == "groq" and os.environ.get("GROQ_API_KEY"):
                        response = await self.groq.chat(fb_model, messages, self.config.temperature)
                        break
                    elif fb_provider == "gemini" and os.environ.get("GEMINI_API_KEY"):
                        response = await self.gemini.chat(fb_model, messages, self.config.temperature)
                        break
                    elif fb_provider == "openrouter":
                        response = await self.openrouter.chat(fb_model, messages, self.config.temperature)
                        break
                except Exception as fb_err:
                    last_error = f"{fb_provider}: {fb_err}"
                    continue
            else:
                # Retry after delay (rate limit recovery)
                import asyncio
                await asyncio.sleep(15)
                try:
                    if os.environ.get("GLM_API_KEY"):
                        response = await self.zhipu.chat("glm-4-flash", messages, self.config.temperature)
                    elif os.environ.get("GROQ_API_KEY"):
                        response = await self.groq.chat("llama-3.3-70b-versatile", messages, self.config.temperature)
                    else:
                        return f"⏳ النموذج مشغول حالياً — حاول مرة أخرى بعد قليل"
                except Exception:
                    return f"⏳ النموذج مشغول حالياً — حاول مرة أخرى بعد قليل"

        # ٦. حفظ الرد
        self.history.append(Message(role="assistant", content=response.content))

        # ٧. تنظيف التاريخ (الذاكرة قصيرة المدى)
        if len(self.history) > self.config.max_history * 2:
            self._compress_history()

        # ٨. تسجيل في الذاكرة (للأوركستريتور فقط)
        if self.memory:
            self.memory.remember(
                f"Q: {message[:100]}\nA: {response.content[:100]}",
                category="conversation",
                importance=2
            )

        return response.content

    async def stream_chat(self, message: str,
                          task_type: str = "chat") -> AsyncGenerator[str, None]:
        """محادثة مع Romih Agent - بالبث المباشر"""
        # ١. فحص الأمان
        if self.shield.detect_distillation(message):
            if self.shield.should_block_distiller():
                yield "⚠️ تم اكتشاف محاولات متكررة."
                return

        # ٢. إضافة للتاريخ
        self.history.append(Message(role="user", content=message))

        # ٣. اختيار النموذج
        model_id, provider = await self.router.route(
            task_type=task_type,
            prefer_local=self.config.prefer_local,
            need_privacy=self.config.need_privacy,
        )

        # ٤. بناء الرسائل
        messages = [{"role": "system", "content": self.system_prompt + self._user_context}]
        for msg in self.history[-self.config.max_history:]:
            messages.append({"role": msg.role, "content": msg.content})

        # ٥. بث مباشر
        full_response = ""
        try:
            if provider == "ollama":
                async for chunk in self.ollama.stream_chat(model_id, messages):
                    full_response += chunk
                    yield chunk
            else:
                async for chunk in self.openrouter.stream_chat(model_id, messages):
                    full_response += chunk
                    yield chunk
        except Exception as e:
            yield f"\n❌ خطأ: {e}"
            return

        # ٦. حفظ الرد
        self.history.append(Message(role="assistant", content=full_response))

    def _compress_history(self):
        """ضغط التاريخ (الذاكرة قصيرة المدى)"""
        # نحتفظ بآخر ٢٠ رسالة فقط
        self.history = self.history[-20:]

    async def execute_goal(self, goal: str) -> str:
        """Execute a multi-step goal using the Agent Loop (Think-Act-Observe)"""
        # Direct tool execution: if goal matches a known tool, run it directly
        direct = self._try_direct_tool(goal)
        if direct:
            # File delivery markers - pass through directly
            if direct.startswith("<<<FILE_"):
                return direct
            # Try to make it natural Arabic via synthesize
            try:
                return await self._synthesize_direct(goal, direct)
            except:
                return direct
        
        if self.loop:
            return await self.loop.execute(goal)
        return await self.chat(goal)

    async def _synthesize_direct(self, goal: str, raw_result: str) -> str:
        """Convert raw tool result to natural Arabic"""
        import json
        try:
            model_id, _ = await self.router.route(task_type="arabic")
            messages = [
                {"role": "system", "content": "You are a helpful Arabic assistant. Convert technical results into a natural, friendly Arabic response. Never output JSON or Python dicts - always natural Arabic."},
                {"role": "user", "content": f"User asked: {goal}\n\nResult: {raw_result[:2000]}\n\nConvert this into a natural Arabic response."}
            ]
            response = await self.openrouter.chat(model_id, messages, 0.3)
            if response.content and len(response.content.strip()) > 10:
                return response.content
        except:
            pass
        return raw_result

    def _try_direct_tool(self, goal: str) -> Optional[str]:
        """If goal text EXPLICITLY contains a known tool name, execute it directly."""
        goal_lower = goal.lower().strip()
        
        # Skip simple responses
        simple_responses = ["نعم", "yes", "لا", "no", "ok", "طيب", "تمام", "يلا", 
                          "go", "start", "اه", "ايوه", "ماشي", "حسنا", "هيا", "بنا"]
        if goal_lower in simple_responses or len(goal_lower) < 4:
            return None
        
        # Only match if first word is a known tool name
        first_word = goal_lower.split()[0] if ' ' in goal_lower else goal_lower
        for tool_name in self.tools.tools:
            if first_word == tool_name or goal_lower.startswith(tool_name + ' '):
                try:
                    params = {}
                    parts = goal.split()
                    for part in parts[1:]:
                        if '=' in part:
                            k, v = part.split('=', 1)
                            params[k] = v
                    result = self.tools.execute(tool_name, params, auto_approve=True)
                    # If result contains a csv marker, pass raw dict for file delivery
                    if isinstance(result, dict) and result.get("csv"):
                        return "<<<FILE_CSV>>>" + json.dumps(result, ensure_ascii=False)
                    return str(result)
                except Exception as e:
                    return f"Tool execution error: {e}"
        return None

    def clear_history(self):
        """مسح المحادثة الحالية"""
        self.history = []
        self._user_context = ""  # per-user memory injection

    def get_status(self) -> dict:
        """حالة الوكيل الحالية"""
        return {
            "name": self.config.name,
            "history_length": len(self.history),
            "prefer_local": self.config.prefer_local,
            "need_privacy": self.config.need_privacy,
            "suspicious_count": self.shield.suspicious_count,
            "distill_attempts": self.shield.distill_attempts,
            "swarm_agents": len(self.swarm.agents) if self.swarm else 0,
            "memory_items": self.memory.long_term.get_stats()["total"] if self.memory else 0,
            "tools_count": len(self.tools.tools) if self.tools else 0,
            "agent_loop": self.loop is not None,
        }


async def demo():
    """عرض توضيحي لـ Romih Agent"""
    print("=" * 50)
    print("🤖 Romih Agent - بكلمتين")
    print("=" * 50)

    agent = RomihAgent(AgentConfig(name="محمد"))

    # اختبار محلي
    print("\n🦙 اختبار Ollama المحلي...")
    agent.config.prefer_local = True
    response = await agent.chat("مرحباً - عرفني بنفسك في جملتين", task_type="arabic")
    print(f"Romih: {response[:200]}...")

    print(f"\n📊 الحالة: {agent.get_status()}")
    print("✅ Romih Agent Core - يعمل بنجاح")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(demo())
