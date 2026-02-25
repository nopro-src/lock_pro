from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_account
from app.api.schemas.locks import LockCreateIn, LockOut, AddMemberIn, MemberOut
from app.services import lock_service
from app.db.repositories import locks_repo

router = APIRouter()


@router.post("", response_model=LockOut)
def create_lock(payload: LockCreateIn, db: Session = Depends(get_db), acc=Depends(get_current_account)):
    lk = lock_service.create_lock_as_owner(db, owner_account_id=acc.id, name=payload.name)
    return LockOut(id=lk.id, name=lk.name, code=lk.code)


@router.get("", response_model=list[LockOut])
def list_my_locks(db: Session = Depends(get_db), acc=Depends(get_current_account)):
    locks = locks_repo.list_locks_for_account(db, acc.id)
    return [LockOut(id=l.id, name=l.name, code=l.code) for l in locks]


@router.post("/{lock_id}/members", response_model=MemberOut)
def add_member(lock_id: int, payload: AddMemberIn, db: Session = Depends(get_db), acc=Depends(get_current_account)):
    mem = lock_service.add_user_to_lock(db, lock_id, owner_account_id=acc.id, email=payload.email, role=payload.role)
    return MemberOut(account_id=mem.account_id, role=mem.role)


@router.get("/{lock_id}/members", response_model=list[MemberOut])
def list_members(lock_id: int, db: Session = Depends(get_db), acc=Depends(get_current_account)):
    # must be a member (owner or user) to view
    if not locks_repo.get_membership(db, lock_id, acc.id):
        from app.core.exceptions import forbidden
        raise forbidden("Not a member of this lock")
    ms = locks_repo.list_members(db, lock_id)
    return [MemberOut(account_id=m.account_id, role=m.role) for m in ms]