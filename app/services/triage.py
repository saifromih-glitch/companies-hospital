"""Triage Engine - analyzes and classifies incoming cases"""
import re

# Sector-specific keywords for smarter triage
SECTOR_KEYWORDS = {
    "finance": ["خسارة", "أرباح", "ميزانية", "تدفق نقدي", "سيولة", "ديون", "تمويل", "استثمار", "مصاريف", "إيرادات", "capital", "cash", "profit"],
    "marketing": ["عملاء", "تسويق", "مبيعات", "إعلان", "سوشال", "انستجرام", "brand", "marketing", "sales", "حملة", "منافس"],
    "operations": ["إنتاج", "مخزون", "توصيل", "سلسلة", "موردين", "جودة", "تأخير", "delivery", "inventory", "supplier", "عملية", "كفاءة"],
    "hr": ["موظفين", "رواتب", "تدريب", "توظيف", "استقالة", "أداء", "hr", "employee", "team", "فريق", "مدير"],
    "strategy": ["خطة", "توسع", "سوق", "منافسة", "رؤية", "نمو", "strategy", "growth", "expansion", "مستقبل"],
    "legal": ["عقد", "قانون", "ترخيص", "دعوى", "محامي", "legal", "contract", "lawsuit", "تنظيم", "لائحة"],
    "technical": ["نظام", "برنامج", "تقنية", "سيرفر", "تطبيق", "أتمتة", "software", "server", "automation", "tech"],
}

SEVERITY_KEYWORDS = {
    "critical": ["كارثة", "انهيار", "إفلاس", "خسارة كبيرة", "وقف", "إغلاق", "طارئ", "عاجل", "خطير جداً"],
    "high": ["خسارة", "انخفاض حاد", "مشكلة كبيرة", "أزمة", "تراجع كبير", "ديون متراكمة", "تهديد"],
    "medium": ["مشكلة", "تحسين", "تطوير", "تراجع", "منافسة", "تحدي", "فرصة"],
    "low": ["استفسار", "سؤال", "استشارة", "فكرة", "اقتراح", "تحسين بسيط"],
}


def triage_case(description: str, category: str) -> dict:
    """Analyze a case description and return severity + keywords + suggested experts."""
    desc_lower = description.lower()

    # 1. Determine severity
    severity = _detect_severity(desc_lower)

    # 2. Extract keywords
    keywords = _extract_keywords(desc_lower, category)

    # 3. Suggest experts
    experts = _suggest_experts(category, severity, keywords)

    return {
        "severity": severity,
        "keywords": keywords,
        "suggested_experts": experts[:5],  # top 5 experts
        "word_count": len(description.split()),
        "category": category,
    }


def _detect_severity(desc: str) -> str:
    for level, words in SEVERITY_KEYWORDS.items():
        for w in words:
            if w in desc:
                return level
    return "medium"


def _extract_keywords(desc: str, category: str) -> list[str]:
    found = []
    # Check category-specific keywords
    for kw in SECTOR_KEYWORDS.get(category, []):
        if kw.lower() in desc:
            found.append(kw)
    # Check all sectors
    for sector, words in SECTOR_KEYWORDS.items():
        if sector != category:
            for w in words:
                if w.lower() in desc and w not in found:
                    found.append(w)
    return found[:10]


def _suggest_experts(category: str, severity: str, keywords: list[str]) -> list[str]:
    """Suggest which experts should analyze this case."""
    # Map categories to primary experts
    expert_map = {
        "finance": ["finance_pro", "data_pro"],
        "marketing": ["growth_hacker", "content_strategist"],
        "operations": ["operations", "data_pro"],
        "hr": ["hr_pro", "resident_mgmt"],
        "strategy": ["strategist", "executive", "resident_mgmt"],
        "legal": ["legal_pro"],
        "technical": ["codemaster", "code_guardian"],
    }

    primary = expert_map.get(category, ["strategist", "data_pro"])

    # Critical/high severity adds more experts
    if severity in ("critical", "high"):
        primary = primary + ["executive", "root_cause", "orchestrator"]

    # Deduplicate while preserving order
    seen = set()
    result = []
    for e in primary:
        if e not in seen:
            seen.add(e)
            result.append(e)
    return result
