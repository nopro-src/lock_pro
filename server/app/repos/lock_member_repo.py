from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.lock_member import LockMember, LockRole


class LockMemberRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_member(self, lock_id: int, account_id: int) -> LockMember | None:
        stmt = select(LockMember).where(LockMember.lock_id == lock_id, LockMember.account_id == account_id)
        return self.db.execute(stmt).scalars().first()

    def list_members(self, lock_id: int) -> list[LockMember]:
        stmt = select(LockMember).where(LockMember.lock_id == lock_id).order_by(LockMember.id.desc())
        return list(self.db.execute(stmt).scalars().all())

    def add_member(self, lock_id: int, account_id: int, role: LockRole) -> LockMember:
        m = LockMember(lock_id=lock_id, account_id=account_id, role=role)
        self.db.add(m)
        self.db.flush()
        return m

    def list_locks_for_account(self, account_id: int) -> list[LockMember]:
        stmt = select(LockMember).where(LockMember.account_id == account_id)
        return list(self.db.execute(stmt).scalars().all())