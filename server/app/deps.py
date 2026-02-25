from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.config import settings
from app.face.registry import get_engine
from app.core.security import decode_token
from app.db.repositories.accounts_repo import get_by_id
from app.core.exceptions import unauthorized
from app.core.ws_manager import WSManager

bearer = HTTPBearer(auto_error=False)
_ws_manager = WSManager()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_face_engine():
    return get_engine(settings.MODEL_KEY)


def get_ws_manager():
    return _ws_manager


def get_current_account(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
):
    if not creds:
        raise unauthorized("Missing token")
    account_id = int(decode_token(creds.credentials))
    acc = get_by_id(db, account_id)
    if not acc:
        raise unauthorized("Account not found")
    if not acc.is_active:
        raise unauthorized("Account inactive")
    return acc