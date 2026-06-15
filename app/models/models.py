"""SQLAlchemy models — Companies Hospital"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


def utcnow():
    return datetime.now(timezone.utc)


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_ar: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(200))
    sector: Mapped[str] = mapped_column(String(50), nullable=False)
    size: Mapped[str] = mapped_column(String(20), nullable=False)
    commercial_reg: Mapped[str | None] = mapped_column(String(20))
    vat_number: Mapped[str | None] = mapped_column(String(15))
    city: Mapped[str | None] = mapped_column(String(50))
    founded_year: Mapped[int | None] = mapped_column(Integer)
    employees_count: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="company")
    cases: Mapped[list["Case"]] = relationship(back_populates="company")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name_ar: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="owner")
    oauth_provider: Mapped[str | None] = mapped_column(String(20))
    oauth_id: Mapped[str | None] = mapped_column(String(255))
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    company: Mapped["Company | None"] = relationship(back_populates="users")


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="triage")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    company: Mapped["Company"] = relationship(back_populates="cases")


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"))
    expert_id: Mapped[str] = mapped_column(String(50), nullable=False)
    analysis: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)
    used_cache: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TreatmentPlan(Base):
    __tablename__ = "treatment_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.id"))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    steps: Mapped[dict] = mapped_column(JSON, nullable=False)
    automations: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    treatment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("treatment_plans.id"))
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"))
    kpi_name: Mapped[str] = mapped_column(String(100), nullable=False)
    kpi_value: Mapped[float | None] = mapped_column(Float)
    kpi_target: Mapped[float | None] = mapped_column(Float)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ErrorMemory(Base):
    __tablename__ = "error_memory"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    wrong_answer: Mapped[str | None] = mapped_column(Text)
    correction: Mapped[str] = mapped_column(Text, nullable=False)
    correction_source: Mapped[str] = mapped_column(String(20), default="system")
    expert_id: Mapped[str | None] = mapped_column(String(50))
    confidence: Mapped[float | None] = mapped_column(Float)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
