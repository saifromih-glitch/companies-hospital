"""مستشفى الشركات — FastAPI Application"""
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

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


# ═══ Static pages ═══
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public")

@app.get("/login")
async def login_page():
    path = os.path.join(FRONTEND_DIR, "login.html")
    if os.path.isfile(path):
        return FileResponse(path, media_type="text/html; charset=utf-8")
    return {"status": "login page not found"}


@app.get("/register")
async def register_company_page():
    path = os.path.join(FRONTEND_DIR, "register-company.html")
    if os.path.isfile(path):
        return FileResponse(path, media_type="text/html; charset=utf-8")
    return {"status": "registration page not found"}


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
