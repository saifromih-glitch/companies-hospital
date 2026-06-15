"""Company endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Company
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/companies", tags=["companies"])


class CompanyCreate(BaseModel):
    name_ar: str
    name_en: str | None = None
    sector: str
    size: str
    city: str | None = None
    founded_year: int | None = None
    employees_count: int | None = None
    commercial_reg: str | None = None
    vat_number: str | None = None


class CompanyResponse(BaseModel):
    id: str
    name_ar: str
    name_en: str | None = None
    sector: str
    size: str
    city: str | None = None
    founded_year: int | None = None
    employees_count: int | None = None


@router.post("", status_code=201)
async def create_company(
    body: CompanyCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """Register a new company."""
    existing = db.query(Company).filter(
        (Company.commercial_reg == body.commercial_reg)
    ).first()
    if existing and body.commercial_reg:
        raise HTTPException(status_code=409, detail="السجل التجاري مسجل مسبقاً")

    company = Company(**body.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)

    # Link user to company
    user.company_id = company.id
    db.commit()

    return CompanyResponse(
        id=str(company.id),
        name_ar=company.name_ar,
        name_en=company.name_en,
        sector=company.sector,
        size=company.size,
        city=company.city,
        founded_year=company.founded_year,
        employees_count=company.employees_count,
    )
