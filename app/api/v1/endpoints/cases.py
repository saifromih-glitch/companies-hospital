"""Case endpoints — the core of Companies Hospital (Triage + Diagnosis)"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Case, Company, Diagnosis
from app.auth.dependencies import get_current_user
from app.services.triage import triage_case
from app.services.experts import analyze_case
from app.services.synthesis import synthesize

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])


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

    # Run expert analysis
    result = analyze_case(
        title=case.title,
        description=case.description,
        category=case.category,
        severity=case.severity,
        sector=company.sector if company else "retail",
        size=company.size if company else "small",
        call_llm=None,  # LLM integration point
    )

    # Synthesize
    synthesis = synthesize(result["analyses"])

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
