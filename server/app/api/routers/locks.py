from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import db_dep
from app.schemas.lock import LockCreateIn, LockOut, MemberAddIn, MemberOut
from app.security.deps import get_current_account
from app.services.lock_service import LockService
from app.exceptions import ConflictError, ForbiddenError, NotFoundError, http_409, http_403, http_404

router = APIRouter(prefix="/api/locks", tags=["locks"])


@router.post("", response_model=LockOut)
def create_lock(payload: LockCreateIn, db: Session = Depends(db_dep), acct=Depends(get_current_account)):
    try:
        lock = LockService(db).create_lock(acct.id, payload.name, payload.code, payload.threshold_override)
        return LockOut(
            id=lock.id,
            name=lock.name,
            code=lock.code,
            owner_id=lock.owner_id,
            threshold_override=lock.threshold_override,
        )
    except ConflictError as e:
        raise http_409(str(e))


@router.get("", response_model=list[LockOut])
def list_locks(db: Session = Depends(db_dep), acct=Depends(get_current_account)):
    locks = LockService(db).list_locks_for_account(acct.id)
    return [
        LockOut(id=l.id, name=l.name, code=l.code, owner_id=l.owner_id, threshold_override=l.threshold_override) for l in locks
    ]


@router.post("/{lock_id}/members", response_model=MemberOut)
def add_member(lock_id: int, payload: MemberAddIn, db: Session = Depends(db_dep), acct=Depends(get_current_account)):
    try:
        m = LockService(db).add_member(lock_id, acct.id, payload.account_id, payload.role)
        return MemberOut(id=m.id, lock_id=m.lock_id, account_id=m.account_id, role=m.role)
    except ForbiddenError as e:
        raise http_403(str(e))
    except ConflictError as e:
        raise http_409(str(e))
    except NotFoundError as e:
        raise http_404(str(e))


@router.get("/{lock_id}/members", response_model=list[MemberOut])
def list_members(lock_id: int, db: Session = Depends(db_dep), acct=Depends(get_current_account)):
    try:
        rows = LockService(db).list_members(lock_id, acct.id)
        return [MemberOut(id=r.id, lock_id=r.lock_id, account_id=r.account_id, role=r.role) for r in rows]
    except ForbiddenError as e:
        raise http_403(str(e))
    except NotFoundError as e:
        raise http_404(str(e))


@router.post("/{lock_id}/open", status_code=status.HTTP_200_OK)
def open_lock(lock_id: int, db: Session = Depends(db_dep), acct=Depends(get_current_account)):
    try:
        LockService(db).open_lock(lock_id, acct.id)
        return {"ok": True, "lock_id": lock_id, "command": "open"}
    except ForbiddenError as e:
        raise http_403(str(e))
    except NotFoundError as e:
        raise http_404(str(e))


@router.post("/{lock_id}/close", status_code=status.HTTP_200_OK)
def close_lock(lock_id: int, db: Session = Depends(db_dep), acct=Depends(get_current_account)):
    try:
        LockService(db).close_lock(lock_id, acct.id)
        return {"ok": True, "lock_id": lock_id, "command": "close"}
    except ForbiddenError as e:
        raise http_403(str(e))
    except NotFoundError as e:
        raise http_404(str(e))