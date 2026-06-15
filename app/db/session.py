"""Database engine and session management"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings

settings = get_settings()

# Only create engine if DATABASE_URL is configured
if settings.database_url:
    engine = create_engine(settings.database_url, echo=settings.debug)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a database session."""
    if not SessionLocal:
        raise RuntimeError("DATABASE_URL not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    if engine:
        Base.metadata.create_all(bind=engine)
