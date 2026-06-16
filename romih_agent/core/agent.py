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
    OllamaConnector, OpenRouterConnector, AutoRouter,
    ModelResponse, ollama, openrouter, router
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
        # Workshop Plugin (enterprise CRM)
        try:
            from plugins.workshop_tools import register as _register_workshop
            _register_workshop(self.tools)
        except Exception:
            pass
        # Agent Loop (think-act-observe)
        self.loop = None
        if create_swarm:
            from core.agent_loop import AgentLoop
            self.loop = AgentLoop(self)
        self.history: list[Message] = []
        self._init_system_prompt()

    def _init_system_prompt(self):
        """تهيئة البرومبت الداخلي - لا يُشارك أبداً"""
        tools_prompt = self.tools.get_tools_prompt() if self.tools else ""
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
1. رد بالعربية الفصحى - لا إنجليزية إلا في الكود
2. للرسوم: استخدم علامة كود svg للرسوم المتجهة
3. كن دقيقاً - لا تتخيل، لا تهلوس
4. لا تذكر أنك "بوت" - أنت وكيل ذكي
5. إذا سألك من أنت: "أنا Romih Agent، وكيلك الذكي"

{tools_prompt}

اسم المستخدم: {self.config.name}"""

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
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in self.history[-self.config.max_history:]:
            messages.append({"role": msg.role, "content": msg.content})

        # ٥. إرسال للنموذج
        try:
            if provider == "ollama":
                response = await self.ollama.chat(
                    model_id, messages, self.config.temperature
                )
            else:
                response = await self.openrouter.chat(
                    model_id, messages, self.config.temperature
                )
        except Exception as e:
            # Fallback: جرب المحلي لو السحابي فشل
            if provider == "openrouter":
                try:
                    local_models = await self.ollama.list_models()
                    if local_models:
                        response = await self.ollama.chat(
                            local_models[0], messages, self.config.temperature
                        )
                    else:
                        return f"❌ خطأ: {e}"
                except Exception as e2:
                    return f"❌ جميع النماذج غير متاحة: {e2}"
            else:
                return f"❌ النموذج المحلي غير متاح: {e}"

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
        messages = [{"role": "system", "content": self.system_prompt}]
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
        if self.loop:
            return await self.loop.execute(goal)
        return await self.chat(goal)

    def clear_history(self):
        """مسح المحادثة الحالية"""
        self.history = []

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
