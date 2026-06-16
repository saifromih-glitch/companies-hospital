"""مستشفى الشركات — FastAPI Application"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
try:
    from app.romih_router import router as romih_router
except Exception as e:
    romih_router = None
    logger.warning(f"Romih Agent skipped: {e}")

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


# ═══ Static pages (embedded — no Docker encoding issues) ═══
try:
    from app.pages import router as pages_router
    app.include_router(pages_router)
    logger.info("Static pages registered")
except Exception as e:
    logger.warning(f"Static pages skipped: {e}")

# ═══ Romih Agent ═══
if romih_router:
    app.include_router(romih_router)
    logger.info("Romih Agent registered")


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

# ═══ Routers ═══
try:
    from app.auth.oauth import router as auth_router
    app.include_router(auth_router)
    logger.info("Auth routes registered")
except Exception as e:
    logger.warning(f"Auth routes skipped: {e}")

try:
    from app.api.v1.endpoints.companies import router as company_router
    app.include_router(company_router)
    logger.info("Company routes registered")
except Exception as e:
    logger.warning(f"Company routes skipped: {e}")

try:
    from app.api.v1.endpoints.cases import router as case_router
    app.include_router(case_router)
    logger.info("Case routes registered")
except Exception as e:
    logger.warning(f"Case routes skipped: {e}")
