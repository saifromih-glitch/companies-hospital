"""Synthesis Engine — merges multiple expert analyses into one coherent diagnosis"""
from collections import Counter


def synthesize(analyses: list[dict], call_llm=None) -> dict:
    """
    Merge multiple expert analyses into one synthesized diagnosis.

    Args:
        analyses: List of {"expert_name": ..., "analysis": ...} dicts
        call_llm: Optional LLM callable for advanced synthesis
    """
    if not analyses:
        return {"synthesis": "لا توجد تحليلات", "confidence": 0.0}

    # 1. Extract key themes
    themes = _extract_themes(analyses)

    # 2. Build consensus score
    consensus = _calc_consensus(analyses)

    # 3. Generate recommendations
    recommendations = _extract_recommendations(analyses)

    # 4. LLM-powered synthesis (if available)
    synthesis_text = ""
    if call_llm:
        synthesis_text = _llm_synthesis(analyses, themes, call_llm)

    return {
        "synthesis": synthesis_text or _template_synthesis(analyses, themes),
        "themes": themes,
        "consensus_score": round(consensus, 2),
        "recommendations": recommendations[:5],
        "expert_count": len(analyses),
    }


def _extract_themes(analyses: list[dict]) -> list[str]:
    """Extract common themes across analyses."""
    theme_keywords = {
        "استراتيجي": ["استراتيج", "سوق", "منافس", "توسع", "نمو"],
        "مالي": ["مال", "إيراد", "تكلف", "ربح", "خسار", "تدفق"],
        "تشغيلي": ["عمل", "إنتاج", "كفاء", "جود", "مخزو"],
        "تقني": ["تقن", "نظام", "برمج", "أتمت"],
        "بشري": ["موظف", "فريق", "تدريب", "موارد", "ثقاف"],
        "قانوني": ["قانون", "عقد", "ترخيص", "امتثال"],
    }

    # Count keyword occurrences
    all_text = " ".join(a.get("analysis", "") for a in analyses)

    theme_scores = {}
    for theme, keywords in theme_keywords.items():
        score = sum(1 for kw in keywords if kw in all_text)
        if score > 0:
            theme_scores[theme] = score

    # Return top themes sorted by score
    return [t for t, _ in sorted(theme_scores.items(), key=lambda x: -x[1])[:4]]


def _calc_consensus(analyses: list[dict]) -> float:
    """Calculate consensus level among experts (0-1)."""
    if len(analyses) < 2:
        return 1.0

    # Simple heuristic: look for overlap in keywords
    all_keywords = []
    for a in analyses:
        words = set(a.get("analysis", "").split())
        all_keywords.append(words)

    if not all_keywords or not all_keywords[0]:
        return 0.0

    # Jaccard-like overlap
    intersection = all_keywords[0]
    union = all_keywords[0]
    for w in all_keywords[1:]:
        intersection = intersection & w
        union = union | w

    return len(intersection) / max(len(union), 1)


def _extract_recommendations(analyses: list[dict]) -> list[str]:
    """Extract actionable recommendations from analyses."""
    recommendations = []
    for a in analyses:
        analysis = a.get("analysis", "")
        # Look for numbered points, bullet points, or "توصية" keywords
        for line in analysis.split("\n"):
            line = line.strip()
            if any(marker in line[:3] for marker in ["1.", "2.", "3.", "-", "*", "•"]):
                recommendations.append({
                    "expert": a.get("expert_name", ""),
                    "recommendation": line.lstrip("123456789.-*• "),
                })

    # If no structured recommendations found, return top analysis excerpts
    if not recommendations:
        for a in analyses:
            analysis = a.get("analysis", "")
            if len(analysis) > 50:
                recommendations.append({
                    "expert": a.get("expert_name", ""),
                    "recommendation": analysis[:200] + "...",
                })

    return recommendations[:5]


def _template_synthesis(analyses: list[dict], themes: list[str]) -> str:
    """Generate a synthesis from templates when LLM is unavailable."""
    expert_names = [a.get("expert_name", "") for a in analyses]

    parts = [
        "تم تحليل الحالة بواسطة " + "، ".join(expert_names) + ".",
        "المجالات الرئيسية: " + "، ".join(themes) + "." if themes else "",
        "مستوى التوافق بين الخبراء: " + ("مرتفع" if _calc_consensus(analyses) > 0.3 else "متفاوت") + ".",
    ]
    return " ".join(p for p in parts if p)


def _llm_synthesis(analyses: list[dict], themes: list[str], call_llm) -> str:
    """Use LLM to synthesize expert analyses."""
    prompt = f"""أنت المنسق العام (🎼 الأوركستريتور) في مستشفى الشركات.

مهمتك: دمج آراء الخبراء في تشخيص واحد متماسك.

الموضوعات الرئيسية: {', '.join(themes)}

آراء الخبراء:
"""
    for a in analyses:
        prompt += f"\n--- {a.get('emoji', '')} {a.get('expert_name', '')} ---\n{a.get('analysis', '')[:500]}"

    prompt += """

اخرج بالصيغة التالية:
## التشخيص الموحد
(فقرة واحدة)

## التوصيات (مرتبة حسب الأولوية)
1. ...
2. ...
3. ...

## درجة الثقة: (عالية / متوسطة / تحتاج مراجعة)

أجب بالعربية فقط."""
    
    try:
        return call_llm(prompt)
    except Exception:
        return _template_synthesis(analyses, themes)
