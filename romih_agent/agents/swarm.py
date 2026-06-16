"""
Romih Agent - Sub-Agent Spawning
=================================
تفريخ وكلاء متخصصين للمهام المعقدة
"""
import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.agent import RomihAgent


@dataclass
class SubAgent:
    name: str
    role: str
    expertise: str
    model_preference: str  # "local" or "cloud"
    agent: "RomihAgent" = None

    def init_agent(self):
        from core.agent import RomihAgent, AgentConfig
        self.agent = RomihAgent(
            AgentConfig(
                name=self.name,
                prefer_local=(self.model_preference == "local"),
            ),
            create_swarm=False  # Sub-agent = عامل، مش أوركستريتور
        )


class AgentSwarm:
    """سرب الوكلاء - يدير الوكلاء الفرعيين"""

    def __init__(self, orchestrator: "RomihAgent"):
        self.orchestrator = orchestrator
        self.agents: dict[str, SubAgent] = {}
        self._init_default_agents()

    def _init_default_agents(self):
        """تهيئة الوكلاء الافتراضيين"""
        defaults = [
            SubAgent("مبرمج", "مبرمج", "Python, JS, FastAPI, Next.js", "local"),
            SubAgent("محلل", "محلل بيانات", "بيانات، أسواق، تقارير", "cloud"),
            SubAgent("ناشر", "ناشر", "Railway, Docker, Vercel, Git", "local"),
            SubAgent("مدقق", "مدقق جودة", "TDD، اختبارات، مراجعة كود", "local"),
            SubAgent("خبير_عربي", "خبير لغة عربية", "ترجمة، تدقيق، RTL", "local"),
        ]
        for agent in defaults:
            agent.init_agent()
            self.agents[agent.name] = agent

    def add_agent(self, name: str, role: str, expertise: str,
                  model_preference: str = "local"):
        agent = SubAgent(name, role, expertise, model_preference)
        agent.init_agent()  # create_swarm=False automatically
        self.agents[name] = agent
        return agent

    async def delegate(self, agent_name: str, task: str) -> str:
        if agent_name not in self.agents:
            return f"❌ وكيل غير موجود: {agent_name}"

        agent = self.agents[agent_name]
        prompt = f"""[دورك: {agent.role}]
[تخصصك: {agent.expertise}]

المهمة: {task}

نفذ المهمة بدقة واحترافية. رد بالعربية."""

        return await agent.agent.chat(prompt, task_type="code")

    async def parallel_delegate(self, tasks: dict[str, str]) -> dict[str, str]:
        async def run_one(name, task):
            result = await self.delegate(name, task)
            return name, result

        results = await asyncio.gather(*[
            run_one(name, task) for name, task in tasks.items()
        ])
        return dict(results)

    def list_agents(self) -> list[dict]:
        return [{
            "name": a.name,
            "role": a.role,
            "expertise": a.expertise,
            "model": "محلي" if a.model_preference == "local" else "سحابي",
            "status": "جاهز" if a.agent else "غير مهيأ"
        } for a in self.agents.values()]
