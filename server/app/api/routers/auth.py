from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_account
from app.api.schemas.auth import RegisterIn, LoginIn, TokenOut, MeOut
from app.services import auth_service

router = APIRouter()


@router.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    acc, token = auth_service.register(db, payload.email, payload.password, payload.full_name)
    return TokenOut(access_token=token)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    acc, token = auth_service.login(db, payload.email, payload.password)
    return TokenOut(access_token=token)


@router.get("/me", response_model=MeOut)
def me(acc=Depends(get_current_account)):
    return MeOut(id=acc.id, email=acc.email, full_name=acc.full_name)