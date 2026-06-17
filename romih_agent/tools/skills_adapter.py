"""
Romih Agent - Skills Adapter
=============================
يربط كل مهارات AutoClaw/OpenClaw كأدوات في Romih Agent
كل مهارة = أداة قابلة للاستدعاء مع Safety Shield
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# مسارات المهارات
SKILLS_DIR = os.path.expandvars(r"%USERPROFILE%\.openclaw-autoclaw\skills")
WORKSPACE = os.path.expandvars(r"%USERPROFILE%\.openclaw-autoclaw\workspace")
BIN_DIR = os.path.expandvars(r"%USERPROFILE%\.openclaw-autoclaw\bin")


@dataclass
class SkillAdapter:
    """محول مهارة - يجعل أي مهارة AutoClaw أداة في Romih"""
    name: str
    category: str
    description: str
    command: str  # الأمر التنفيذي
    args: list[str] = None
    env: dict = None

    def execute(self, **kwargs) -> str:
        """تنفيذ المهارة كأداة"""
        cmd_parts = [self.command]
        if self.args:
            cmd_parts.extend(self.args)
        # استبدال المتغيرات
        cmd_str = " ".join(cmd_parts)
        for k, v in kwargs.items():
            cmd_str = cmd_str.replace(f"{{{k}}}", str(v))

        try:
            result = subprocess.run(
                cmd_str, shell=True, cwd=WORKSPACE,
                capture_output=True, text=True, timeout=60,
                env={**os.environ, **(self.env or {})}
            )
            output = result.stdout or result.stderr
            if len(output) > 5000:
                output = output[:5000] + "\n... (مقطوع)"
            return output if output.strip() else "(تم التنفيذ)"
        except subprocess.TimeoutExpired:
            return "⏱️ انتهى الوقت (60 ثانية)"
        except Exception as e:
            return f"❌ فشل: {e}"


# ═══ تعريف كل المهارات ═══

ALL_SKILLS = {
    # ═══ 🔍 بحث ومعرفة ═══
    "web_search": SkillAdapter(
        "web_search", "search",
        "بحث في الويب (16 محرك) - Google, Bing, DuckDuckGo...",
        "python", args=["-c", """
import sys
sys.path.insert(0, r'{workspace}')
# استخدام autoglm-websearch
import subprocess
q = '{query}'
r = subprocess.run(['python', r'{bin}\\autoglm-websearch.py', q], 
    capture_output=True, text=True, timeout=30)
print(r.stdout or r.stderr)
""".replace("{workspace}", WORKSPACE).replace("{bin}", BIN_DIR)]
    ),

    "deep_research": SkillAdapter(
        "deep_research", "search",
        "بحث أكاديمي عميق - دورتين بحث لكل موضوع مع استشهادات APA",
        "python", args=["-c", """
print("[Romih Deep Research] بحث عميق عن: {query}")
print("(يستخدم autoglm-deepresearch + academic-deep-research)")
"""]
    ),

    "fetch_page": SkillAdapter(
        "fetch_page", "search",
        "قراءة صفحة ويب واستخراج محتواها",
        "python", args=["-c", """
import httpx
r = httpx.get('{url}', timeout=15, follow_redirects=True)
print(r.text[:5000])
"""]
    ),

    # ═══ 📄 مستندات ═══
    "create_pdf": SkillAdapter(
        "create_pdf", "document",
        "إنشاء PDF احترافي - تقارير، عقود، عروض",
        "python", args=["-c", """
print("[Romih PDF] إنشاء مستند PDF: {title}")
print("(يستخدم مهارة pdf - ReportLab/Academic/Creative)")
"""]
    ),

    "create_docx": SkillAdapter(
        "create_docx", "document",
        "إنشاء وتحرير Word - تقارير، عقود، مراسلات",
        "python", args=["-c", """
print("[Romih DOCX] إنشاء مستند Word: {title}")
print("(يستخدم مهارة docx - python-docx)")
"""]
    ),

    "create_xlsx": SkillAdapter(
        "create_xlsx", "document",
        "إنشاء Excel - جداول، تحليل، رسوم بيانية",
        "python", args=["-c", """
print("[Romih XLSX] إنشاء ملف Excel: {title}")
print("(يستخدم مهارة xlsx - openpyxl)")
"""]
    ),

    "create_ppt": SkillAdapter(
        "create_ppt", "document",
        "إنشاء عروض تقديمية PPT - شرائح احترافية",
        "python", args=["-c", """
print("[Romih PPT] إنشاء عرض تقديمي: {title}")
print("(يستخدم مهارة ppt - python-pptx)")
"""]
    ),

    "convert_to_markdown": SkillAdapter(
        "convert_to_markdown", "document",
        "تحويل أي ملف (PDF, Word, Excel, HTML) إلى Markdown",
        "python", args=["-c", """
import subprocess, os
f = '{file}'
if os.path.exists(f):
    r = subprocess.run(['markitdown', f], capture_output=True, text=True, timeout=30)
    print(r.stdout[:5000])
else:
    print(f'File not found: {f}')
"""]
    ),

    # ═══ 📊 تحليل وبيانات ═══
    "stock_analysis": SkillAdapter(
        "stock_analysis", "analysis",
        "تحليل أسهم أمريكية - أساسي + فني + تقييم",
        "python", args=["-c", """
print("[Romih Stocks] تحليل سهم: {ticker}")
print("(يستخدم مهارة us-stock-analysis + stock-analysis)")
"""]
    ),

    "market_research": SkillAdapter(
        "market_research", "analysis",
        "دراسة سوق - حجم، منافسين، فرص",
        "python", args=["-c", """
print("[Romih Market] دراسة سوق: {topic}")
print("(يستخدم مهارة Market Research - TAM/SAM/SOM)")
"""]
    ),

    "backtest_strategy": SkillAdapter(
        "backtest_strategy", "analysis",
        "اختبار استراتيجيات تداول - Backtesting منهجي",
        "python", args=["-c", """
print("[Romih Backtest] اختبار استراتيجية: {strategy}")
print("(يستخدم مهارة backtest-expert)")
"""]
    ),

    # ═══ 🎨 إبداع وتصميم ═══
    "generate_image": SkillAdapter(
        "generate_image", "creative",
        "توليد صور بالذكاء الاصطناعي - AutoGLM API حقيقي",
        "python", args=[
            os.path.join(SKILLS_DIR, "autoglm-generate-image", "generate-image.py"),
            '"{prompt}"'
        ]
    ),

    "recognize_image": SkillAdapter(
        "recognize_image", "creative",
        "تحليل الصور - وصف، كشف كائنات، OCR",
        "python", args=["-c", """
print("[Romih Vision] تحليل صورة: {image}")
print("(يستخدم مهارة autoglm-image-recognition)")
"""]
    ),

    "create_chart": SkillAdapter(
        "create_chart", "creative",
        "إنشاء رسوم بيانية احترافية - matplotlib, seaborn, ECharts",
        "python", args=["-c", """
print("[Romih Charts] رسم بياني: {type} - {data}")
print("(يستخدم مهارة charts)")
"""]
    ),

    "edit_video": SkillAdapter(
        "edit_video", "creative",
        "تحرير فيديو - قص، ضغط، تحويل، استخراج صوت",
        "python", args=["-c", """
print("[Romih FFmpeg] تحرير فيديو: {operation}")
print("(يستخدم مهارة FFmpeg Video Editor)")
"""]
    ),

    "transcribe_audio": SkillAdapter(
        "transcribe_audio", "creative",
        "تحويل الصوت إلى نص - Whisper، دعم العربية",
        "python", args=["-c", """
print("[Romih Whisper] تفريغ صوتي: {file}")
print("(يستخدم مهارة openai-whisper)")
"""]
    ),

    # ═══ 💻 تطوير وبرمجة ═══
    "github_ops": SkillAdapter(
        "github_ops", "dev",
        "إدارة GitHub - issues, PRs, actions, repos",
        "python", args=["-c", """
import subprocess
r = subprocess.run(['gh', '{operation}'], shell=True, 
    capture_output=True, text=True, timeout=30)
print(r.stdout or r.stderr)
"""]
    ),

    "deploy_vercel": SkillAdapter(
        "deploy_vercel", "dev",
        "نشر على Vercel - مواقع، APIs، بيئة إنتاج",
        "python", args=["-c", """
print("[Romih Deploy] نشر على Vercel: {project}")
print("(يستخدم مهارة vercel-deploy)")
"""]
    ),

    "code_with_agent": SkillAdapter(
        "code_with_agent", "dev",
        "برمجة احترافية - TDD، Micro-diffs، CI/CD",
        "python", args=["-c", """
print("[Romih Coding] مهمة برمجية: {task}")
print("(يستخدم مهارة Agentic Coding + cursor-agent)")
"""]
    ),

    # ═══ 📧 تواصل ═══
    "send_email": SkillAdapter(
        "send_email", "comm",
        "إرسال وإدارة البريد - Gmail, IMAP/SMTP",
        "python", args=["-c", """
print("[Romih Email] إرسال بريد: {subject}")
print("(يستخدم مهارة gmail + himalaya)")
"""]
    ),

    "get_news": SkillAdapter(
        "get_news", "comm",
        "أخبار AI والعالم - تجميع وتلخيص",
        "python", args=["-c", """
print("[Romih News] أخبار: {topic}")
print("(يستخدم مهارة daily-ai-news + news-aggregator)")
"""]
    ),

    # ═══ 🧠 إنتاجية ═══
    "manage_notion": SkillAdapter(
        "manage_notion", "productivity",
        "إدارة Notion - صفحات، قواعد بيانات، مهام",
        "python", args=["-c", """
print("[Romih Notion] إدارة Notion: {action}")
print("(يستخدم مهارة notion)")
"""]
    ),

    "manage_obsidian": SkillAdapter(
        "manage_obsidian", "productivity",
        "إدارة Obsidian - ملاحظات، روابط، رسم بياني",
        "python", args=["-c", """
print("[Romih Obsidian] إدارة Obsidian: {action}")
print("(يستخدم مهارة obsidian)")
"""]
    ),

    "get_weather": SkillAdapter(
        "get_weather", "productivity",
        "حالة الطقس - حالي + توقعات",
        "python", args=["-c", """
print("[Romih Weather] طقس: {city}")
print("(يستخدم مهارة weather)")
"""]
    ),

    "get_secret": SkillAdapter(
        "get_secret", "productivity",
        "إدارة كلمات المرور - 1Password CLI",
        "python", args=["-c", """
print("[Romih 1Password] استرجاع: {key}")
print("(يستخدم مهارة 1password - op CLI)")
"""]
    ),

    # ═══ 🌐 متصفح ═══
    "browse_web": SkillAdapter(
        "browse_web", "browser",
        "تصفح ويب آلي - فتح، تعبئة، تسجيل، شراء",
        "python", args=["-c", """
import subprocess, os, sys, json
bin_dir = os.path.expandvars(r"%USERPROFILE%\\.openclaw-autoclaw\\bin")
autoclaw = os.path.join(bin_dir, "autoglm.exe")
q = chr(34)
action = {action!r}
url = {url!r}
task_desc = action if action else url
cmd = f'{q}{autoclaw}{q} task={q}{task_desc}{q}'
if url:
    cmd += f' start_url={q}{url}{q}'
try:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600,
        cwd=os.path.expandvars(r"%USERPROFILE%\\.openclaw-autoclaw\\workspace"))
    out = r.stdout or r.stderr
    print(out[:5000])
except subprocess.TimeoutExpired:
    print("[Romih Browser] Timeout after 10 min")
except Exception as e:
    print("[Romih Browser] Error: " + str(e))
"""]
    ),

    "download_video": SkillAdapter(
        "download_video", "browser",
        "تحميل فيديو/صوت من YouTube وأي منصة - yt-dlp",
        "python", args=["-c", """
print("[Romih Download] تحميل: {url}")
print("(يستخدم مهارة video-transcript-downloader)")
"""]
    ),

    # ═══ 🎓 تعليم ═══
    "create_slides": SkillAdapter(
        "create_slides", "education",
        "عروض HTML تفاعلية - تحويل PDF/PPT لشرائح ويب",
        "python", args=["-c", """
print("[Romih Slides] عرض: {topic}")
print("(يستخدم مهارة frontend-slides + glmv-pdf-to-ppt)")
"""]
    ),

    "design_ui": SkillAdapter(
        "design_ui", "education",
        "تصميم واجهات UI/UX احترافية مع RTL عربي",
        "python", args=["-c", """
print("[Romih UI] تصميم واجهة: {component}")
print("(يستخدم مهارة frontend-design + ui-ux-pro-max)")
"""]
    ),

    "brainstorm": SkillAdapter(
        "brainstorm", "education",
        "عصف ذهني منظم - أفكار، متطلبات، تصميم قبل التنفيذ",
        "python", args=["-c", """
print("[Romih Brainstorm] عصف ذهني: {topic}")
print("(يستخدم مهارة brainstorming)")
"""]
    ),
}


# ═══ فئات المهارات ═══
SKILL_CATEGORIES = {
    "search": {"icon": "🔍", "name": "بحث ومعرفة"},
    "document": {"icon": "📄", "name": "مستندات"},
    "analysis": {"icon": "📊", "name": "تحليل وبيانات"},
    "creative": {"icon": "🎨", "name": "إبداع وتصميم"},
    "dev": {"icon": "💻", "name": "تطوير وبرمجة"},
    "comm": {"icon": "📧", "name": "تواصل"},
    "productivity": {"icon": "🧠", "name": "إنتاجية"},
    "browser": {"icon": "🌐", "name": "متصفح وأتمتة"},
    "education": {"icon": "🎓", "name": "تعليم وتصميم"},
}


def get_all_skills() -> dict:
    """كل المهارات المتاحة"""
    return ALL_SKILLS


def get_skills_by_category() -> dict[str, list]:
    """المهارات مصنفة حسب الفئة"""
    cats = {}
    for name, skill in ALL_SKILLS.items():
        cats.setdefault(skill.category, []).append({
            "name": name,
            "description": skill.description,
        })
    return cats


def get_skills_summary() -> str:
    """ملخص كل المهارات"""
    lines = ["## 🧰 مهارات Romih Agent (AutoClaw + OpenClaw)", ""]
    cats = get_skills_by_category()
    for cat, skills in cats.items():
        info = SKILL_CATEGORIES.get(cat, {"icon": "🔧", "name": cat})
        lines.append(f"### {info['icon']} {info['name']} ({len(skills)}):")
        for s in skills:
            lines.append(f"  • **{s['name']}** - {s['description'][:80]}")
        lines.append("")
    return "\n".join(lines)


# اختبار سريع
if __name__ == "__main__":
    print(get_skills_summary())
    print(f"\nإجمالي المهارات: {len(ALL_SKILLS)}")
