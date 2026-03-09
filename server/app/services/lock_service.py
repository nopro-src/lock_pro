from __future__ import annotations

from sqlalchemy.orm import Session

from app.repos.lock_repo import LockRepo
from app.repos.lock_member_repo import LockMemberRepo
from app.models.lock_member import LockRole
from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.security.rbac import has_at_least


class LockService:
    def __init__(self, db: Session):
        self.db = db
        self.locks = LockRepo(db)
        self.members = LockMemberRepo(db)

    def create_lock(self, owner_id: int, name: str, code: str, threshold_override: float | None):
        if self.locks.get_by_code(code):
            raise ConflictError("Lock code already exists")
        lock = self.locks.create(name=name, code=code, owner_id=owner_id, threshold_override=threshold_override)
        # ensure owner in lock_members too
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
            # owner_id bypass
            if lock.owner_id == account_id:
                return LockRole.OWNER
            raise ForbiddenError("Not a member of this lock")

        if not has_at_least(m.role, required):
            raise ForbiddenError("Insufficient role")
        return m.role

    def add_member(self, lock_id: int, actor_id: int, account_id: int, role: LockRole):
        # only OWNER/ADMIN can add members; ADMIN cannot add OWNER
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
        # naive: load each lock via repo.get (OK for demo; production => join query)
        extra = []
        for lid in member_lock_ids:
            l = self.locks.get(lid)
            if l and l.owner_id != account_id:
                extra.append(l)
        return owned + extra
    # #new
    # def list_locks_dashboard(self, db, owner_id: int):
    #     locks = self.lock_repo.list_by_owner(db, owner_id)
    #     result = []

    #     for lock in locks:
    #         device = self.device_repo.get_by_lock_id(db, lock.id)
    #         member_count = self.lock_member_repo.count_by_lock_id(db, lock.id)

    #         result.append({
    #             "id": lock.id,
    #             "name": lock.name,
    #             "location": getattr(lock, "location", None),
    #             "status": getattr(lock, "status", "active"),
    #             "device_status": getattr(device, "status", None) if device else "offline",
    #             "last_seen_at": getattr(device, "last_seen_at", None) if device else None,
    #             "member_count": member_count,
    #         })

    #     return result