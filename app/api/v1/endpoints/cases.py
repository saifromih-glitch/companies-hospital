"""Case endpoints — the core of Companies Hospital (Triage + Diagnosis)"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Case, Company, Diagnosis
from app.auth.dependencies import get_current_user
from app.services.triage import triage_case
from app.services.experts import analyze_case
from app.services.synthesis import synthesize
from app.services.llm import generate as llm_generate

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])


async def _sync_llm(prompt: str) -> str:
    """Call LLM (async) — bridge for sync expert engine."""
    try:
        return await llm_generate(prompt)
    except Exception as e:
        return f"[خطأ LLM: {e}]"


async def _run_expert_analysis(case: Case, company: Company) -> dict:
    """Run experts one-by-one (sequential) using async LLM."""
    import time
    from app.services.experts import get_experts_for_case, EXPERTS

    experts = get_experts_for_case(case.category, case.severity)
    analyses = []
    total_time = 0

    for expert in experts:
        prompt = expert.prompt_template.format(
            name=expert.name_ar,
            emoji=expert.emoji,
            specialty=expert.specialty,
            title=case.title,
            description=case.description,
            sector=company.sector if company else "retail",
            size=company.size if company else "small",
        )

        start = time.time()
        try:
            response = await llm_generate(prompt)
        except Exception as e:
            response = f"[خطأ: {e}]"
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
        "case": {"title": case.title, "category": case.category, "severity": case.severity},
        "experts_invoked": [e.id for e in experts],
        "total_time_ms": int(total_time * 1000),
        "analyses": analyses,
    }


async def _run_synthesis(analyses: list[dict]) -> dict:
    """Synthesize expert analyses using LLM."""
    from app.services.synthesis import _extract_themes, _calc_consensus, _extract_recommendations

    themes = _extract_themes(analyses)
    consensus = _calc_consensus(analyses)
    recommendations = _extract_recommendations(analyses)

    # LLM synthesis
    synthesis_text = await _llm_synthesis(analyses, themes)

    return {
        "synthesis": synthesis_text or _template_synthesis(analyses, themes),
        "themes": themes,
        "consensus_score": round(consensus, 2),
        "recommendations": recommendations[:5],
        "expert_count": len(analyses),
    }


async def _llm_synthesis(analyses: list[dict], themes: list[str]) -> str:
    """Use LLM to synthesize expert analyses."""
    from app.services.synthesis import _template_synthesis
    
    if not analyses:
        return ""
    
    prompt = f"""أنت المنسق العام (🎼 الأوركستريتور) في مستشفى الشركات.

مهمتك: دمج آراء الخبراء في تشخيص واحد متماسك.

الموضوعات الرئيسية: {', '.join(themes) if themes else 'عام'}

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
        return await llm_generate(prompt, max_tokens=800)
    except Exception:
        return _template_synthesis(analyses, themes)


class CaseCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=300)
    description: str = Field(..., min_length=20)
    category: str  # finance, marketing, operations, hr, strategy, legal, technical, growth
    severity: str | None = None  # auto-set by triage


class CaseResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    severity: str
    status: str
    triage_result: dict | None = None


@router.post("", status_code=201)
async def create_case(
    body: CaseCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """Submit a new case to the hospital. Goes through Triage automatically."""
    if not user.company_id:
        raise HTTPException(status_code=400, detail="يرجى تسجيل الشركة أولاً")

    company = db.query(Company).filter(Company.id == user.company_id).first()
    if not company:
        raise HTTPException(status_code=400, detail="الشركة غير موجودة")

    # Triage: auto-analyze severity and category
    triage_result = triage_case(body.description, body.category)

    case = Case(
        company_id=company.id,
        title=body.title,
        description=body.description,
        category=body.category,
        severity=triage_result.get("severity", "medium"),
        status="triage_complete",
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    return {
        "id": str(case.id),
        "title": case.title,
        "description": case.description,
        "category": case.category,
        "severity": case.severity,
        "status": case.status,
        "triage_result": triage_result,
    }


@router.get("")
async def list_cases(
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """List all cases for the authenticated user's company."""
    if not user.company_id:
        return {"cases": [], "total": 0}

    cases = (
        db.query(Case)
        .filter(Case.company_id == user.company_id)
        .order_by(Case.created_at.desc())
        .all()
    )

    return {
        "cases": [
            {
                "id": str(c.id),
                "title": c.title,
                "category": c.category,
                "severity": c.severity,
                "status": c.status,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in cases
        ],
        "total": len(cases),
    }


@router.post("/{case_id}/diagnose")
async def diagnose_case(
    case_id: str,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """Run the expert pipeline on a case and return the synthesized diagnosis."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="الحالة غير موجودة")
    if str(case.company_id) != str(user.company_id):
        raise HTTPException(status_code=403, detail="غير مصرح")

    company = db.query(Company).filter(Company.id == case.company_id).first()

    # Run expert analysis with LLM (async)
    result = await _run_expert_analysis(case, company)

    # Synthesize with LLM
    synthesis = await _run_synthesis(result["analyses"])

    # Update case status
    case.status = "diagnosed"

    # Store diagnoses
    for analysis in result["analyses"]:
        diag = Diagnosis(
            case_id=case.id,
            expert_id=analysis["expert_id"],
            analysis=analysis["analysis"],
        )
        db.add(diag)

    db.commit()

    return {
        "case_id": str(case.id),
        "status": case.status,
        "diagnosis": synthesis,
        "analyses": result["analyses"],
    }
