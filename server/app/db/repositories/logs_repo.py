from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models import AccessLog


def create_log(db: Session, lock_id: int, matched_account_id: int | None, score: float, success: bool, source: str) -> AccessLog:
    lg = AccessLog(lock_id=lock_id, matched_account_id=matched_account_id, score=score, success=success, source=source)
    db.add(lg)
    db.commit()
    db.refresh(lg)
    return lg


def list_logs(db: Session, lock_id: int, limit: int = 50) -> list[AccessLog]:
    return list(
        db.execute(
            select(AccessLog).where(AccessLog.lock_id == lock_id).order_by(AccessLog.id.desc()).limit(limit)
        ).scalars().all()
    )