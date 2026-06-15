"""مستشفى الشركات — FastAPI Application"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url=None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "platform": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "database_configured": bool(settings.database_url),
    }


@app.on_event("startup")
async def startup():
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database configured: {bool(settings.database_url)}")
    
    # Initialize database tables
    if settings.database_url:
        try:
            from app.models import models  # noqa: F401
            from app.db.session import init_db
            init_db()
            logger.info("Database tables initialized")
        except Exception as e:
            logger.warning(f"Database init skipped: {e}")
