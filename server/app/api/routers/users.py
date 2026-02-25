from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import db_dep
from app.schemas.account import UserCreateIn, UserOut
from app.security.deps import get_current_account
from app.services.user_service import UserService
from app.exceptions import ConflictError, http_409, http_403

router = APIRouter(prefix="/api/users", tags=["users"])


def require_owner(acct) -> None:
    # Global OWNER concept not in schema; we treat "system owner" as first admin in dev OR just allow any logged in?
    # For strictness: only account_id==1 is OWNER in system context (demo).
    # Production: add global roles table. Here keep lightweight.
    if acct.id != 1:
        raise http_403("OWNER only (demo rule: account id=1)")


@router.post("", response_model=UserOut)
def create_user(payload: UserCreateIn, db: Session = Depends(db_dep), acct=Depends(get_current_account)):
    require_owner(acct)
    try:
        u = UserService(db).create_user(payload.email, payload.password, payload.full_name, payload.is_active)
        return UserOut(id=u.id, email=u.email, full_name=u.full_name, is_active=u.is_active)
    except ConflictError as e:
        raise http_409(str(e))


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(db_dep),
    acct=Depends(get_current_account),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    require_owner(acct)
    rows = UserService(db).list_users(limit=limit, offset=offset)
    return [UserOut(id=r.id, email=r.email, full_name=r.full_name, is_active=r.is_active) for r in rows]