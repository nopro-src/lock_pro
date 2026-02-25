from __future__ import annotations

from sqlalchemy.orm import Session

from app.repos.access_log_repo import AccessLogRepo
from app.services.lock_service import LockService
from app.models.lock_member import LockRole


class LogService:
    def __init__(self, db: Session):
        self.db = db
        self.logs = AccessLogRepo(db)
        self.locks = LockService(db)

    def list_logs(self, lock_id: int, actor_id: int, limit: int = 200, offset: int = 0):
        self.locks.require_member_role(lock_id, actor_id, LockRole.ADMIN)
        return self.logs.list_by_lock(lock_id, limit=limit, offset=offset)