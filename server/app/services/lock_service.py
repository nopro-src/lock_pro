from __future__ import annotations

from sqlalchemy.orm import Session

from app.repos.lock_repo import LockRepo
from app.repos.lock_member_repo import LockMemberRepo
from app.models.lock_member import LockRole
from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.security.rbac import has_at_least
from app.services.device_service import DeviceService


class LockService:
    def __init__(self, db: Session):
        self.db = db
        self.locks = LockRepo(db)
        self.members = LockMemberRepo(db)

    def create_lock(self, owner_id: int, name: str, code: str, threshold_override: float | None):
        if self.locks.get_by_code(code):
            raise ConflictError("Lock code already exists")
        lock = self.locks.create(name=name, code=code, owner_id=owner_id, threshold_override=threshold_override)
        if not self.members.get_member(lock.id, owner_id):
            self.members.add_member(lock.id, owner_id, LockRole.OWNER)
        self.db.commit()
        return lock

    def require_member_role(self, lock_id: int, account_id: int, required: LockRole) -> LockRole:
        lock = self.locks.get(lock_id)
        if not lock:
            raise NotFoundError("Lock not found")

        m = self.members.get_member(lock_id, account_id)
        if not m:
            if lock.owner_id == account_id:
                return LockRole.OWNER
            raise ForbiddenError("Not a member of this lock")

        if not has_at_least(m.role, required):
            raise ForbiddenError("Insufficient role")
        return m.role

    def _ensure_can_control(self, lock_id: int, account_id: int):
        lock = self.locks.get(lock_id)
        if not lock:
            raise NotFoundError("Lock not found")

        if lock.owner_id == account_id:
            return lock

        m = self.members.get_member(lock_id, account_id)
        if not m:
            raise ForbiddenError("Not a member of this lock")

        return lock

    def add_member(self, lock_id: int, actor_id: int, account_id: int, role: LockRole):
        actor_role = self.require_member_role(lock_id, actor_id, LockRole.ADMIN)
        if actor_role == LockRole.ADMIN and role == LockRole.OWNER:
            raise ForbiddenError("ADMIN cannot assign OWNER role")

        if self.members.get_member(lock_id, account_id):
            raise ConflictError("Member already exists")

        row = self.members.add_member(lock_id, account_id, role)
        self.db.commit()
        return row

    def list_members(self, lock_id: int, actor_id: int):
        self.require_member_role(lock_id, actor_id, LockRole.ADMIN)
        return self.members.list_members(lock_id)

    def list_locks_for_account(self, account_id: int):
        owned = self.locks.list_for_account(account_id)
        member_rows = self.members.list_locks_for_account(account_id)
        member_lock_ids = {m.lock_id for m in member_rows}
        extra = []
        for lid in member_lock_ids:
            l = self.locks.get(lid)
            if l and l.owner_id != account_id:
                extra.append(l)
        return owned + extra

    def open_lock(self, lock_id: int, actor_id: int):
        self._ensure_can_control(lock_id, actor_id)
        DeviceService(self.db).send_lock_command(lock_id=lock_id, command="open")
        return True

    def close_lock(self, lock_id: int, actor_id: int):
        self._ensure_can_control(lock_id, actor_id)
        DeviceService(self.db).send_lock_command(lock_id=lock_id, command="close")
        return True