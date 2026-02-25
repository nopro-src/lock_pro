from __future__ import annotations

from datetime import datetime, timedelta, timezone
from jose import jwt
from pydantic import BaseModel

from app.config import settings


class JwtPayload(BaseModel):
    sub: str  # account_id
    exp: int
    role: str | None = None  # optional global role if ever needed


def create_access_token(account_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(account_id),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALG)


def decode_token(token: str) -> JwtPayload:
    data = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALG])
    return JwtPayload(**data)