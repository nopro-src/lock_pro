from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_account
from app.api.schemas.logs import LogOut
from app.db.repositories import logs_repo, locks_repo

router = APIRouter()


@router.get("/{lock_id}", response_model=list[LogOut])
def list_logs(lock_id: int, limit: int = 50, db: Session = Depends(get_db), acc=Depends(get_current_account)):
    if not locks_repo.get_membership(db, lock_id, acc.id):
        from app.core.exceptions import forbidden
        raise forbidden("Not a member of this lock")

    logs = logs_repo.list_logs(db, lock_id=lock_id, limit=limit)
    return [
        LogOut(
            id=l.id,
            lock_id=l.lock_id,
            matched_account_id=l.matched_account_id,
            score=l.score,
            success=l.success,
            source=l.source,
            created_at=l.created_at,
        )
        for l in logs
    ]