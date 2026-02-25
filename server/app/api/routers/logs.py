from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import db_dep
from app.schemas.logs import AccessLogOut
from app.security.deps import get_current_account
from app.services.log_service import LogService
from app.exceptions import ForbiddenError, NotFoundError, http_403, http_404

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("/{lock_id}", response_model=list[AccessLogOut])
def list_logs(
    lock_id: int,
    db: Session = Depends(db_dep),
    acct=Depends(get_current_account),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    try:
        rows = LogService(db).list_logs(lock_id, acct.id, limit=limit, offset=offset)
        return [
            AccessLogOut(
                id=r.id,
                lock_id=r.lock_id,
                matched_account_id=r.matched_account_id,
                score=r.score,
                threshold_used=r.threshold_used,
                success=r.success,
                source=r.source.value,
                device_id=r.device_id,
                created_at=r.created_at,
            )
            for r in rows
        ]
    except ForbiddenError as e:
        raise http_403(str(e))
    except NotFoundError as e:
        raise http_404(str(e))