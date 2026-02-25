from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_dep
from app.schemas.auth import RegisterIn, LoginIn, TokenOut, MeOut
from app.security.deps import get_current_account
from app.services.auth_service import AuthService
from app.exceptions import ConflictError, ForbiddenError, http_409, http_403

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=MeOut)
def register(payload: RegisterIn, db: Session = Depends(db_dep)):
    try:
        acct = AuthService(db).register(payload.email, payload.password, payload.full_name)
        return MeOut(id=acct.id, email=acct.email, full_name=acct.full_name, is_active=acct.is_active)
    except ConflictError as e:
        raise http_409(str(e))


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(db_dep)):
    try:
        token = AuthService(db).login(payload.email, payload.password)
        return TokenOut(access_token=token)
    except ForbiddenError as e:
        raise http_403(str(e))


@router.get("/me", response_model=MeOut)
def me(acct=Depends(get_current_account)):
    return MeOut(id=acct.id, email=acct.email, full_name=acct.full_name, is_active=acct.is_active)