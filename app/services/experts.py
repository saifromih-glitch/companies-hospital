"""Expert Engine — 22 AI Experts with personas and analysis pipeline"""
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

# ═══ Expert Definitions ═══

@dataclass
class Expert:
    id: str
    name_ar: str
    emoji: str
    specialty: str
    prompt_template: str
    category: str  # primary category


EXPERTS = {
    "strategist": Expert(
        id="strategist", name_ar="المحلل الإستراتيجي", emoji="🧭",
        specialty="تحليل السوق والاستراتيجية",
        category="strategy",
        prompt_template="""أنت {name} ({emoji}) — خبير {specialty}.
مهمتك: تحليل حالة شركة من منظور إستراتيجي.
الشركة في قطاع: {sector} | حجم: {size}
الحالة: {title}
الوصف: {description}

حلل:
1. الموقف التنافسي
2. الفرص والتهديدات
3. التوصيات الإستراتيجية (٣ نقاط)

أسلوبك: مايكل بورتر — Five Forces + Strategic Positioning.
أجب بالعربية فقط. مباشر، مختصر، بالنقاط."""
    ),
    "executive": Expert(
        id="executive", name_ar="المستشار التنفيذي", emoji="🎓",
        specialty="الإدارة التنفيذية واتخاذ القرار",
        category="strategy",
        prompt_template="""أنت {name} ({emoji}) — خبير {specialty}.
حلل هذه الحالة من منظور تنفيذي.

الشركة: قطاع {sector} | حجم: {size}
الحالة: {title}
الوصف: {description}

اطرح ٥ أسئلة دراكر الأساسية على هذه الحالة، ثم قدم رؤية تنفيذية من ٣ نقاط.
أجب بالعربية. مباشر، عملي."""
    ),
    "finance_pro": Expert(
        id="finance_pro", name_ar="المحلل المالي", emoji="💰",
        specialty="التحليل المالي والتقييم",
        category="finance",
        prompt_template="""أنت {name} ({emoji}) — خبير {specialty}.
حلل الحالة من منظور مالي.

الحالة: {title}
الوصف: {description}

قدم:
1. تحليل مالي (إيرادات، تكاليف، هوامش)
2. ٣ مؤشرات مالية يجب تتبعها
3. توصيات مالية محددة

أسلوبك: أسواث داموداران — DCF + WACC + NPV.
أجب بالعربية. أرقام ونسب."""
    ),
    "operations": Expert(
        id="operations", name_ar="مهندس العمليات", emoji="⚙️",
        specialty="العمليات وتحسين الكفاءة",
        category="operations",
        prompt_template="""أنت {name} ({emoji}) — خبير {specialty}.
حلل الحالة من منظور العمليات.

الحالة: {title}
الوصف: {description}

حدد:
1. عنق الزجاجة (Bottleneck)
2. القيود (Constraints)
3. خطة تحسين من ٣ خطوات

أسلوبك: إلياهو جولدرات — Theory of Constraints.
أجب بالعربية. عملي ومباشر."""
    ),
    "hr_pro": Expert(
        id="hr_pro", name_ar="مستشار الموارد البشرية", emoji="👥",
        specialty="الموارد البشرية والثقافة التنظيمية",
        category="hr",
        prompt_template="""أنت {name} ({emoji}) — خبير {specialty}.
حلل الحالة من منظور الموارد البشرية.

الحالة: {title}
الوصف: {description}

حلل:
1. الجانب البشري للمشكلة
2. توصيات لتحسين الأداء والثقافة
3. مقاييس HR المناسبة

أسلوبك: لازلو بوك — People Analytics + Google 10X.
أجب بالعربية. مبني على البيانات."""
    ),
    "codemaster": Expert(
        id="codemaster", name_ar="مهندس التقنية", emoji="💻",
        specialty="الهندسة البرمجية والتقنية",
        category="technical",
        prompt_template="""أنت {name} ({emoji}) — خبير {specialty}.
حلل الحالة من منظور تقني.

الحالة: {title}
الوصف: {description}

قدم:
1. تحليل تقني للمشكلة
2. حلول تقنية مقترحة
3. تقدير التكلفة والوقت

أسلوبك: مارتن فاولر — Microservices + CI/CD.
أجب بالعربية. تقني دقيق."""
    ),
    "legal_pro": Expert(
        id="legal_pro", name_ar="المستشار القانوني", emoji="⚖️",
        specialty="القانون والامتثال",
        category="legal",
        prompt_template="""أنت {name} ({emoji}) — خبير {specialty}.
حلل الحالة من منظور قانوني ونظامي.

الحالة: {title}
الوصف: {description}

حلل في ٣ أبعاد: قانوني / تقني / مستقبلي.
أسلوبك: ريتشارد سسكند — LegalTech.
أجب بالعربية."""
    ),
    "growth_hacker": Expert(
        id="growth_hacker", name_ar="مستشار النمو", emoji="📈",
        specialty="النمو والتسويق",
        category="marketing",
        prompt_template="""أنت {name} ({emoji}) — خبير {specialty}.
حلل حالة الشركة من منظور النمو.

الحالة: {title}
الوصف: {description}

طبق Pirate Metrics (AARRR):
1. Acquisition — اكتساب العملاء
2. Activation — تفعيل
3. Retention — احتفاظ
4. Revenue — إيرادات
5. Referral — إحالات

أسلوبك: شون إليس — North Star Metric.
أجب بالعربية."""
    ),
}

# Secondary experts (available for synthesis)
SUPPORT_EXPERTS = [
    Expert(id="data_pro", name_ar="عالم البيانات", emoji="📊",
           specialty="تحليل البيانات", category="data",
           prompt_template="حلل البيانات. أسلوب DJ Patil."),
    Expert(id="code_guardian", name_ar="حارس الكود", emoji="🐛",
           specialty="جودة البرمجيات", category="technical",
           prompt_template="اختبر الكود. أسلوب Kent Beck TDD."),
    Expert(id="resident_mgmt", name_ar="مستشار الإدارة", emoji="🏛️",
           specialty="الإدارة المؤسسية", category="strategy",
           prompt_template="حلل الإدارة. أسلوب Jim Collins."),
    Expert(id="root_cause", name_ar="محلل الأسباب الجذرية", emoji="🎯",
           specialty="تحليل جذور المشكلات", category="operations",
           prompt_template="5 Whys + Ishikawa. أسلوب Kaoru Ishikawa."),
    Expert(id="orchestrator", name_ar="مهندس النظم", emoji="🎼",
           specialty="تكامل النظم", category="technical",
           prompt_template="The Three Ways. أسلوب Gene Kim."),
    Expert(id="content_strategist", name_ar="استراتيجي المحتوى", emoji="📝",
           specialty="استراتيجية المحتوى", category="marketing",
           prompt_template="خطة محتوى. أسلوب content marketing."),
]

ALL_EXPERTS = {**EXPERTS, **{e.id: e for e in SUPPORT_EXPERTS}}


# ═══ Expert Pipeline ═══

def get_experts_for_case(category: str, severity: str) -> list[Expert]:
    """Select experts to analyze a case based on category and severity."""
    selected = []
    for exp in EXPERTS.values():
        if exp.category == category:
            selected.append(exp)

    # Add primary expert if none matched
    if not selected:
        selected.append(EXPERTS["strategist"])

    # Critical/high adds more experts
    if severity in ("critical", "high"):
        selected.append(EXPERTS["executive"])
        selected.append(ALL_EXPERTS["root_cause"])

    return selected


def analyze_case(
    title: str,
    description: str,
    category: str,
    severity: str,
    sector: str = "retail",
    size: str = "small",
    call_llm=None,  # callable: (prompt) -> str
) -> dict:
    """
    Run the full expert analysis pipeline on a case.

    Args:
        call_llm: Function that takes a prompt and returns a response.
                  If None, returns the prompts without analysis.
    """
    experts = get_experts_for_case(category, severity)

    analyses = []
    total_time = 0

    for expert in experts:
        prompt = expert.prompt_template.format(
            name=expert.name_ar,
            emoji=expert.emoji,
            specialty=expert.specialty,
            title=title,
            description=description,
            sector=sector,
            size=size,
        )

        start = time.time()
        if call_llm:
            try:
                response = call_llm(prompt)
            except Exception as e:
                response = f"[خطأ: {e}]"
        else:
            response = "[بانتظار تفعيل LLM]"

        elapsed = time.time() - start
        total_time += elapsed

        analyses.append({
            "expert_id": expert.id,
            "expert_name": expert.name_ar,
            "emoji": expert.emoji,
            "analysis": response,
            "time_ms": int(elapsed * 1000),
        })

    return {
        "case": {"title": title, "category": category, "severity": severity},
        "experts_invoked": [e.id for e in experts],
        "total_time_ms": int(total_time * 1000),
        "analyses": analyses,
    }
