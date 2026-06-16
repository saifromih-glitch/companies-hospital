"""
Romih Agent — Tool Registry
============================
سجل الأدوات — File, Shell, Web, Git, Code
كل أداة تمر على Safety Shield قبل التنفيذ
"""
import os
import subprocess
import json
from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    LOW = "low"         # آمن — قراءة ملفات، list
    MEDIUM = "medium"   # يحتاج مراقبة — كتابة ملفات، git status
    HIGH = "high"       # يحتاج تأكيد — حذف، تشغيل أوامر
    CRITICAL = "critical"  # ممنوع إلا بأمر مباشر


@dataclass
class ToolParam:
    name: str
    type: str  # str, int, bool, path
    description: str
    required: bool = True
    default: Any = None


@dataclass
class Tool:
    name: str
    description: str
    category: str  # file, shell, web, git, code
    risk: RiskLevel
    params: list[ToolParam] = field(default_factory=list)
    execute: Callable = None
    requires_approval: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "risk": self.risk.value,
            "params": [
                {"name": p.name, "type": p.type,
                 "description": p.description, "required": p.required}
                for p in self.params
            ],
            "requires_approval": self.requires_approval,
        }


# ═══ تعريف الأدوات ═══

def _tool_read_file(path: str) -> str:
    """قراءة ملف"""
    if not os.path.exists(path):
        return f"❌ الملف غير موجود: {path}"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if len(content) > 5000:
        content = content[:5000] + f"\n... (مقطوع — {len(content)} حرف)"
    return content


def _tool_write_file(path: str, content: str) -> str:
    """كتابة ملف"""
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"✅ تمت كتابة {len(content)} حرف إلى {path}"


def _tool_list_files(path: str = ".") -> str:
    """عرض محتويات مجلد"""
    if not os.path.exists(path):
        return f"❌ المسار غير موجود: {path}"
    items = os.listdir(path)
    result = []
    for item in sorted(items):
        full = os.path.join(path, item)
        prefix = "📁" if os.path.isdir(full) else "📄"
        size = os.path.getsize(full) if os.path.isfile(full) else 0
        result.append(f"  {prefix} {item} ({_fmt_size(size)})")
    return f"📂 {path}:\n" + "\n".join(result[:50])


def _tool_delete_file(path: str) -> str:
    """حذف ملف"""
    if not os.path.exists(path):
        return f"❌ الملف غير موجود: {path}"
    os.remove(path)
    return f"🗑️ تم حذف: {path}"


def _tool_run_shell(command: str, cwd: str = ".") -> str:
    """تشغيل أمر في الطرفية"""
    try:
        result = subprocess.run(
            command, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout or result.stderr
        if len(output) > 3000:
            output = output[:3000] + f"\n... (مقطوع)"
        return output if output else "(لا يوجد مخرج)"
    except subprocess.TimeoutExpired:
        return "⏱️ انتهى الوقت (30 ثانية)"
    except Exception as e:
        return f"❌ خطأ: {e}"


def _tool_web_fetch(url: str) -> str:
    """جلب صفحة ويب"""
    import httpx
    try:
        r = httpx.get(url, timeout=15, follow_redirects=True)
        return r.text[:5000]
    except Exception as e:
        return f"❌ فشل جلب {url}: {e}"


def _tool_git_status(path: str = ".") -> str:
    """حالة Git"""
    return _tool_run_shell("git status --short", cwd=path)


def _tool_git_commit(message: str, path: str = ".") -> str:
    """Git commit"""
    return _tool_run_shell(f'git add -A && git commit -m "{message}"', cwd=path)


def _fmt_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.0f}{unit}"
        size /= 1024
    return f"{size:.0f}TB"


# ═══ سجل الأدوات ═══

class ToolRegistry:
    """سجل الأدوات — يربط كل أداة بـ Safety Shield"""

    def __init__(self, safety_shield=None, include_skills: bool = True):
        self.tools: dict[str, Tool] = {}
        self.shield = safety_shield
        self._register_defaults()
        if include_skills:
            self._register_skills()
            self._register_local_agents()
            self._register_rabie_brain()

    def _register_defaults(self):
        """تسجيل الأدوات الافتراضية"""
        defaults = [
            # 📁 ملفات
            Tool("read_file", "قراءة محتوى ملف", "file", RiskLevel.LOW,
                 [ToolParam("path", "str", "مسار الملف")],
                 _tool_read_file),
            Tool("write_file", "كتابة محتوى إلى ملف", "file", RiskLevel.MEDIUM,
                 [ToolParam("path", "str", "مسار الملف"),
                  ToolParam("content", "str", "المحتوى")],
                 _tool_write_file),
            Tool("list_files", "عرض محتويات مجلد", "file", RiskLevel.LOW,
                 [ToolParam("path", "str", "مسار المجلد", required=False, default=".")],
                 _tool_list_files),
            Tool("delete_file", "حذف ملف", "file", RiskLevel.HIGH,
                 [ToolParam("path", "str", "مسار الملف")],
                 _tool_delete_file, requires_approval=True),

            # 🖥️ طرفية
            Tool("run_shell", "تشغيل أمر في الطرفية", "shell", RiskLevel.HIGH,
                 [ToolParam("command", "str", "الأمر"),
                  ToolParam("cwd", "str", "مجلد العمل", required=False, default=".")],
                 _tool_run_shell, requires_approval=True),

            # 🌐 ويب
            Tool("web_fetch", "جلب صفحة ويب", "web", RiskLevel.LOW,
                 [ToolParam("url", "str", "رابط الصفحة")],
                 _tool_web_fetch),

            # 📦 Git
            Tool("git_status", "حالة Git", "git", RiskLevel.LOW,
                 [ToolParam("path", "str", "مسار المستودع", required=False, default=".")],
                 _tool_git_status),
            Tool("git_commit", "حفظ التغييرات في Git", "git", RiskLevel.MEDIUM,
                 [ToolParam("message", "str", "رسالة commit"),
                  ToolParam("path", "str", "مسار المستودع", required=False, default=".")],
                 _tool_git_commit, requires_approval=True),
        ]
        for tool in defaults:
            self.register(tool)

    def register(self, tool: Tool):
        """تسجيل أداة جديدة"""
        self.tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def list_by_category(self) -> dict[str, list[dict]]:
        """عرض الأدوات حسب الفئة"""
        cats = {}
        for tool in self.tools.values():
            cats.setdefault(tool.category, []).append(tool.to_dict())
        return cats

    def list_all(self) -> list[dict]:
        return [t.to_dict() for t in self.tools.values()]

    def execute(self, tool_name: str, params: dict,
                auto_approve: bool = False) -> str:
        """
        تنفيذ أداة مع فحص الأمان.
        
        Args:
            tool_name: اسم الأداة
            params: المعاملات
            auto_approve: تجاوز طلب الموافقة (للمستخدم المالك فقط)
        """
        tool = self.get(tool_name)
        if not tool:
            return f"❌ أداة غير معروفة: {tool_name}\nالأدوات المتاحة: {', '.join(self.tools.keys())}"

        # ١. فحص المخاطر عبر Safety Shield
        if self.shield and tool.risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            command_str = f"{tool_name} {json.dumps(params)}"
            decision = self.shield.evaluate(command_str)
            if decision.risk == "BLOCKED":
                return f"🛡️ ممنوع: {decision.reason}"

        # ٢. طلب موافقة للأدوات عالية الخطورة
        if tool.requires_approval and not auto_approve:
            return (f"⚠️ هذه الأداة تحتاج موافقة:\n"
                    f"   الأداة: {tool_name}\n"
                    f"   المعاملات: {params}\n"
                    f"   استخدم auto_approve=True للتنفيذ")

        # ٣. تحضير المعاملات
        kwargs = {}
        for param in tool.params:
            value = params.get(param.name, param.default)
            if param.required and value is None:
                return f"❌ المعامل {param.name} مطلوب"
            if value is not None:
                kwargs[param.name] = value

        # ٤. تنفيذ
        try:
            result = tool.execute(**kwargs)
            return result
        except Exception as e:
            return f"❌ فشل تنفيذ {tool_name}: {e}"

    def _register_skills(self):
        """Register AutoClaw/OpenClaw skills as tools"""
        from tools.skills_adapter import ALL_SKILLS

        skills = [
            # (skill_name, tool_name, description, category, risk, params_list, needs_approval)
            ("web_search", "web_search", "Web search (16 engines)", "search", "LOW",
                [("query", "str", "Search query")], False),
            ("deep_research", "deep_research", "Academic deep research + APA", "search", "LOW",
                [("query", "str", "Research topic")], False),
            ("fetch_page", "fetch_page", "Read full webpage content", "search", "LOW",
                [("url", "str", "Page URL")], False),
            ("create_pdf", "create_pdf", "Create professional PDF", "document", "MEDIUM",
                [("title", "str", "Document title"), ("content", "str", "Content", False, "")], False),
            ("create_docx", "create_docx", "Create and edit Word docs", "document", "MEDIUM",
                [("title", "str", "Document title"), ("content", "str", "Content", False, "")], False),
            ("create_xlsx", "create_xlsx", "Create Excel with charts", "document", "MEDIUM",
                [("title", "str", "File title"), ("data", "str", "Data", False, "")], False),
            ("create_ppt", "create_ppt", "Create PowerPoint slides", "document", "MEDIUM",
                [("title", "str", "Presentation title"), ("content", "str", "Content", False, "")], False),
            ("convert_to_markdown", "convert_to_markdown", "Convert any file to Markdown", "document", "LOW",
                [("file", "str", "File path")], False),
            ("stock_analysis", "stock_analysis", "Stock analysis - fundamental + technical", "analysis", "LOW",
                [("ticker", "str", "Stock ticker (AAPL, TSLA...)")], False),
            ("market_research", "market_research", "Market research - TAM/SAM/SOM", "analysis", "LOW",
                [("topic", "str", "Research topic")], False),
            ("backtest_strategy", "backtest_strategy", "Backtest trading strategies", "analysis", "LOW",
                [("strategy", "str", "Strategy description")], False),
            ("generate_image", "generate_image", "AI image generation", "creative", "LOW",
                [("prompt", "str", "Image description")], False),
            ("recognize_image", "recognize_image", "Image analysis + Arabic OCR", "creative", "LOW",
                [("image", "str", "Image path or URL")], False),
            ("create_chart", "create_chart", "Professional charts and diagrams", "creative", "LOW",
                [("type", "str", "Chart type (bar, line, pie...)"), ("data", "str", "Chart data")], False),
            ("edit_video", "edit_video", "Video editing - FFmpeg", "creative", "MEDIUM",
                [("operation", "str", "FFmpeg operation")], False),
            ("transcribe_audio", "transcribe_audio", "Audio transcription - Whisper", "creative", "MEDIUM",
                [("file", "str", "Audio file path")], False),
            ("github_ops", "github_ops", "GitHub CLI operations", "dev", "MEDIUM",
                [("operation", "str", "GitHub operation")], False),
            ("deploy_vercel", "deploy_vercel", "Deploy to Vercel", "dev", "HIGH",
                [("project", "str", "Project name")], True),
            ("code_with_agent", "code_with_agent", "Professional TDD coding", "dev", "MEDIUM",
                [("task", "str", "Coding task")], False),
            ("send_email", "send_email", "Email - Gmail/IMAP", "comm", "MEDIUM",
                [("subject", "str", "Email subject")], False),
            ("get_news", "get_news", "AI and world news", "comm", "LOW",
                [("topic", "str", "News topic", False, "AI")], False),
            ("get_weather", "get_weather", "Weather - current + forecast", "productivity", "LOW",
                [("city", "str", "City name", False, "Makkah")], False),
            ("get_secret", "get_secret", "1Password CLI", "productivity", "HIGH",
                [("key", "str", "Secret key name")], True),
            ("manage_notion", "manage_notion", "Notion management", "productivity", "MEDIUM",
                [("action", "str", "Notion action")], False),
            ("manage_obsidian", "manage_obsidian", "Obsidian management", "productivity", "MEDIUM",
                [("action", "str", "Obsidian action")], False),
            ("browse_web", "browse_web", "Automated web browsing", "browser", "HIGH",
                [("url", "str", "Page URL"), ("action", "str", "Browser action")], True),
            ("download_video", "download_video", "Download video - yt-dlp", "browser", "MEDIUM",
                [("url", "str", "Video URL")], False),
            ("create_slides", "create_slides", "Interactive HTML slides", "education", "MEDIUM",
                [("topic", "str", "Presentation topic")], False),
            ("design_ui", "design_ui", "UI/UX design + RTL Arabic", "education", "MEDIUM",
                [("component", "str", "UI component")], False),
            ("brainstorm", "brainstorm", "Structured brainstorming", "education", "LOW",
                [("topic", "str", "Brainstorm topic")], False),
        ]

        for (skill_name, name, desc, cat, risk_str, params_raw, needs_approval) in skills:
            if skill_name in ALL_SKILLS:
                skill = ALL_SKILLS[skill_name]
                risk = getattr(RiskLevel, risk_str)
                params = []
                for p in params_raw:
                    required = True if len(p) == 3 else p[3]
                    default = p[4] if len(p) == 5 else None
                    params.append(ToolParam(p[0], p[1], p[2], required, default))
                def make_exec(s=skill):
                    return lambda **kw: s.execute(**kw)
                tool = Tool(name, desc, cat, risk, params, make_exec())
                tool.requires_approval = needs_approval
                self.register(tool)


    def _register_local_agents(self):
        """Register Hermes, Mimo, Pi Agent as tools"""
        from tools.local_agents import ALL_LOCAL_SKILLS

        local_tools = [
            # Hermes Agent v0.15.2
            ("hermes_code", "hermes_code", "Hermes: Full coding task (analyze-build-test)", "dev", "MEDIUM",
                [("task", "str", "Programming task"), ("model", "str", "Model", False, "ollama/gemma4:12b")], False),
            ("hermes_refactor", "hermes_refactor", "Hermes: Refactor and improve code", "dev", "MEDIUM",
                [("file_path", "str", "File to refactor"), ("instructions", "str", "Refactoring instructions")], False),
            ("hermes_debug", "hermes_debug", "Hermes: Debug from error logs", "dev", "LOW",
                [("error_log", "str", "Error log"), ("file_path", "str", "File path", False, "")], False),
            ("hermes_dashboard", "hermes_dashboard", "Hermes: Open web dashboard (port 9120)", "dev", "LOW",
                [("port", "int", "Port", False, 9120)], False),

            # Mimo v0.1.1
            ("mimo_plan", "mimo_plan", "Mimo: Project planning and analysis", "dev", "MEDIUM",
                [("project_description", "str", "Project description")], False),
            ("mimo_execute", "mimo_execute", "Mimo: Execute plan and build", "dev", "HIGH",
                [("task_description", "str", "Build task")], True),
            ("mimo_build", "mimo_build", "Mimo: Build complete project from scratch", "dev", "HIGH",
                [("task", "str", "What to build"), ("framework", "str", "Framework", False, "nextjs")], True),

            # Pi Agent v0.1.0
            ("pi_agent_run", "pi_agent_run", "Pi Agent: Agent Loop with tools", "dev", "MEDIUM",
                [("task", "str", "Agent task"), ("tools", "str", "Tools", False, "")], False),
            ("pi_agent_swarm", "pi_agent_swarm", "Pi Agent: Parallel agent swarm", "dev", "MEDIUM",
                [("task", "str", "Swarm task"), ("num_agents", "int", "Number of agents", False, 3)], False),
        ]

        for (skill_name, name, desc, cat, risk_str, params_raw, needs_approval) in local_tools:
            if skill_name in ALL_LOCAL_SKILLS:
                skill_def = ALL_LOCAL_SKILLS[skill_name]
                risk = getattr(RiskLevel, risk_str)
                params = []
                for p in params_raw:
                    required = True if len(p) == 3 else p[3]
                    default = p[4] if len(p) == 5 else None
                    params.append(ToolParam(p[0], p[1], p[2], required, default))
                fn = skill_def["execute"]
                tool = Tool(name, desc, cat, risk, params, fn)
                tool.requires_approval = needs_approval
                self.register(tool)


    def _register_rabie_brain(self):
        """Register Rabie Brain - 17 experts + 8 methodologies"""
        from tools.rabie_brain import EXPERTS, METHODOLOGIES, consult_expert, apply_methodology, get_all_experts, get_all_methodologies

        rabie_tools = [
            ("consult_expert", "Rabie: Consult a legendary expert", "brain", "LOW",
                [("expert_key", "str", "Expert (strategist, finance, codemaster...)"),
                 ("problem", "str", "Problem to analyze")], consult_expert, False),
            ("apply_methodology", "Rabie: Apply a methodology", "brain", "LOW",
                [("methodology_key", "str", "Methodology (north_star, debug_methodology...)"),
                 ("context", "str", "Context", False, "")], apply_methodology, False),
            ("list_experts", "Rabie: List all 17 experts", "brain", "LOW",
                [], lambda **kw: get_all_experts(), False),
            ("list_methodologies", "Rabie: List all 8 methodologies", "brain", "LOW",
                [], lambda **kw: get_all_methodologies(), False),
        ]

        for (name, desc, cat, risk_str, params_raw, fn, needs_approval) in rabie_tools:
            risk = getattr(RiskLevel, risk_str)
            params = []
            for p in params_raw:
                required = True if len(p) == 3 else p[3]
                default = p[4] if len(p) == 5 else None
                params.append(ToolParam(p[0], p[1], p[2], required, default))
            tool = Tool(name, desc, cat, risk, params, fn)
            tool.requires_approval = needs_approval
            self.register(tool)

        # Ponytail - lazy senior dev
        try:
            from tools.rabie_brain import ponytail_check
            tool = Tool("ponytail_check", "Ponytail: 6-step ladder before writing code", "brain", RiskLevel.LOW,
                [ToolParam("task", "str", "Task to analyze")], ponytail_check)
            self.register(tool)
        except Exception:
            pass


    def get_tools_prompt(self) -> str:
        """نص الأدوات لاستخدامه في System Prompt"""
        lines = ["## الأدوات المتاحة:"]
        for tool in self.tools.values():
            risk_icon = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
            icon = risk_icon.get(tool.risk.value, "⚪")
            params_str = ", ".join(
                f"{p.name}:{p.type}" + ("?" if not p.required else "")
                for p in tool.params
            )
            lines.append(f"{icon} **{tool.name}**({params_str}) — {tool.description}")
        return "\n".join(lines)

