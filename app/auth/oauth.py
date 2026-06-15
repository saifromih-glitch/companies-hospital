"""Google OAuth + Email/Password + JWT Authentication"""
import os
import secrets
import re
from datetime import datetime, timedelta, timezone

import httpx
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.models.models import User
from app.auth.dependencies import get_current_user

# Fix Arabic encoding in JSON responses
import json as _json
from fastapi.responses import Response as _Response

def _arabic_json(data, status_code=200):
    """Return JSON with proper UTF-8 encoding for Arabic."""
    return _Response(
        content=_json.dumps(data, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
        status_code=status_code,
    )

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
settings = get_settings()

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

SCOPE = "openid email profile"


def create_jwt(user_id: str, email: str, name: str) -> str:
    """Create a JWT token for the authenticated user."""
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_jwt(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(status_code=401, detail="رمز الدخول غير صالح")


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency — returns the authenticated user."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="يرجى تسجيل الدخول")

    token = auth_header.replace("Bearer ", "")
    payload = decode_jwt(token)
    user_id = payload.get("sub")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="المستخدم غير موجود")

    return user


@router.get("/google/login")
async def google_login():
    """Redirect user to Google OAuth consent screen."""
    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth غير مهيأ")

    state = secrets.token_hex(16)
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": f"{os.environ.get('APP_URL', 'https://companies-hospital-production.up.railway.app')}/api/v1/auth/google/callback",
        "response_type": "code",
        "scope": SCOPE,
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url=f"{GOOGLE_AUTH_URL}?{qs}")


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback — create/link user, return JWT."""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="رمز التفويض مفقود")

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": f"{os.environ.get('APP_URL', 'https://companies-hospital-production.up.railway.app')}/api/v1/auth/google/callback",
        })
        tokens = token_resp.json()
        access_token = tokens.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="فشل التحقق من جوجل")

        # Get user info
        user_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info = user_resp.json()

    google_id = user_info.get("sub")
    email = user_info.get("email")
    name = user_info.get("name", email)

    if not email:
        raise HTTPException(status_code=400, detail="لم يتم الحصول على البريد الإلكتروني")

    # Find or create user
    user = db.query(User).filter(
        (User.oauth_provider == "google") & (User.oauth_id == google_id)
    ).first()

    if not user:
        # Check if email exists
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Link Google to existing account
            user.oauth_provider = "google"
            user.oauth_id = google_id
        else:
            user = User(
                email=email,
                name_ar=name,
                oauth_provider="google",
                oauth_id=google_id,
            )
            db.add(user)

    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    # Create JWT
    token = create_jwt(str(user.id), user.email, user.name_ar)

    return _arabic_json({
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name_ar,
        },
    })


# ═══ Email/Password Auth ═══

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@router.post("/register")
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email and password."""
    if not EMAIL_REGEX.match(body.email):
        raise HTTPException(status_code=400, detail="صيغة البريد الإلكتروني غير صحيحة")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="كلمة المرور يجب أن تكون ٨ أحرف على الأقل")
    if len(body.name.strip()) < 2:
        raise HTTPException(status_code=400, detail="الاسم قصير جداً")

    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="البريد الإلكتروني مسجل مسبقاً")

    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    
    user = User(
        email=body.email,
        name_ar=body.name,
        oauth_provider="email",
        oauth_id=hashed,  # store hashed password as oauth_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_jwt(str(user.id), user.email, user.name_ar)
    return JSONResponse({
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name_ar,
        },
    }, status_code=201)


@router.post("/login")
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(User).filter(
        User.email == body.email,
        User.oauth_provider == "email",
    ).first()

    if not user or not user.oauth_id:
        raise HTTPException(status_code=401, detail="البريد الإلكتروني أو كلمة المرور غير صحيحة")

    if not bcrypt.checkpw(body.password.encode(), user.oauth_id.encode()):
        raise HTTPException(status_code=401, detail="البريد الإلكتروني أو كلمة المرور غير صحيحة")

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    token = create_jwt(str(user.id), user.email, user.name_ar)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name_ar,
        },
    }


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    """Return current authenticated user info."""
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name_ar,
        "role": user.role,
        "company_id": str(user.company_id) if user.company_id else None,
    }
