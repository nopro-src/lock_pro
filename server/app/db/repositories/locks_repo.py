from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models import Lock, LockMember


def create_lock(db: Session, name: str, code: str) -> Lock:
    lk = Lock(name=name, code=code)
    db.add(lk)
    db.commit()
    db.refresh(lk)
    return lk


def get_lock(db: Session, lock_id: int) -> Lock | None:
    return db.get(Lock, lock_id)


def list_locks_for_account(db: Session, account_id: int) -> list[Lock]:
    rows = db.execute(
        select(Lock).join(LockMember, LockMember.lock_id == Lock.id).where(LockMember.account_id == account_id)
    ).scalars().all()
    return list(rows)


def add_member(db: Session, lock_id: int, account_id: int, role: str) -> LockMember:
    mem = LockMember(lock_id=lock_id, account_id=account_id, role=role)
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return mem


def get_membership(db: Session, lock_id: int, account_id: int) -> LockMember | None:
    return db.execute(
        select(LockMember).where(LockMember.lock_id == lock_id, LockMember.account_id == account_id)
    ).scalar_one_or_none()


def list_members(db: Session, lock_id: int) -> list[LockMember]:
    return list(db.execute(select(LockMember).where(LockMember.lock_id == lock_id)).scalars().all())


def remove_member(db: Session, lock_id: int, account_id: int) -> None:
    mem = get_membership(db, lock_id, account_id)
    if mem:
        db.delete(mem)
        db.commit()