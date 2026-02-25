from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.access_log import AccessLog, AccessSource


class AccessLogRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        lock_id: int,
        matched_account_id: int | None,
        score: float,
        threshold_used: float,
        success: bool,
        source: AccessSource,
        device_id: int | None,
    ) -> AccessLog:
        row = AccessLog(
            lock_id=lock_id,
            matched_account_id=matched_account_id,
            score=score,
            threshold_used=threshold_used,
            success=success,
            source=source,
            device_id=device_id,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list_by_lock(self, lock_id: int, limit: int = 200, offset: int = 0) -> list[AccessLog]:
        stmt = (
            select(AccessLog)
            .where(AccessLog.lock_id == lock_id)
            .order_by(AccessLog.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.execute(stmt).scalars().all())