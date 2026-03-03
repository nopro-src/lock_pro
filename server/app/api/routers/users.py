from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import db_dep
from app.exceptions import ConflictError, NotFoundError, http_403, http_404, http_409
from app.models.account import GlobalRole
from app.schemas.account import UserCreateIn, UserOut
from app.security.deps import get_current_account
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


def require_global_owner(acct) -> None:
    role = acct.global_role.value if hasattr(acct.global_role, "value") else acct.global_role
    if role != GlobalRole.OWNER and role != "OWNER":
        raise http_403("OWNER only (global_role=OWNER)")


@router.post("", response_model=UserOut)
def create_user(
    payload: UserCreateIn,
    db: Session = Depends(db_dep),
    acct=Depends(get_current_account),
):
    require_global_owner(acct)
    try:
        u = UserService(db).create_user(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            is_active=payload.is_active,
            lock_id=payload.lock_id,
        )
        return UserOut(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            is_active=u.is_active,
            global_role=str(u.global_role.value if hasattr(u.global_role, "value") else u.global_role),
        )
    except ConflictError as e:
        raise http_409(str(e))
    except NotFoundError as e:
        raise http_404(str(e))


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(db_dep),
    acct=Depends(get_current_account),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    require_global_owner(acct)
    rows = UserService(db).list_users(limit=limit, offset=offset)
    return [
        UserOut(
            id=r.id,
            email=r.email,
            full_name=r.full_name,
            is_active=r.is_active,
            global_role=str(r.global_role.value if hasattr(r.global_role, "value") else r.global_role),
        )
        for r in rows
    ]