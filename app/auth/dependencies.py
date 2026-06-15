"""Auth dependencies and middleware"""
from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.models.models import User

settings = get_settings()


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(status_code=401, detail="رمز الدخول غير صالح أو منتهي")


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency — returns the authenticated user. Returns 401 if not authenticated."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="يرجى تسجيل الدخول")

    token = auth_header.replace("Bearer ", "")
    payload = decode_token(token)
    user_id = payload.get("sub")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="المستخدم غير موجود")

    return user


async def get_optional_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """Like get_current_user but returns None instead of 401 if not authenticated."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    try:
        token = auth_header.replace("Bearer ", "")
        payload = decode_token(token)
        user_id = payload.get("sub")
        return db.query(User).filter(User.id == user_id).first()
    except (HTTPException, JWTError):
        return None
