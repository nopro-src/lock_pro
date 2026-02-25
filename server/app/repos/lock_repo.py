from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.lock import Lock


class LockRepo:
    def __init__(self, db: Session):
        self.db = db

    def get(self, lock_id: int) -> Lock | None:
        return self.db.get(Lock, lock_id)

    def get_by_code(self, code: str) -> Lock | None:
        stmt = select(Lock).where(Lock.code == code)
        return self.db.execute(stmt).scalars().first()

    def create(self, name: str, code: str, owner_id: int, threshold_override: float | None) -> Lock:
        lock = Lock(name=name, code=code, owner_id=owner_id, threshold_override=threshold_override)
        self.db.add(lock)
        self.db.flush()
        return lock

    def list_for_account(self, account_id: int) -> list[Lock]:
        # show locks owned or member of (handled in service using lock_members)
        stmt = select(Lock).where(Lock.owner_id == account_id).order_by(Lock.id.desc())
        return list(self.db.execute(stmt).scalars().all())

    def list_all(self, limit: int = 200, offset: int = 0) -> list[Lock]:
        stmt = select(Lock).order_by(Lock.id.desc()).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())