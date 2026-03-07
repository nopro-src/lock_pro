from __future__ import annotations

from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.models.account import GlobalRole
from app.models.lock_member import LockRole
from app.repos.account_repo import AccountRepo
from app.repos.lock_member_repo import LockMemberRepo
from app.repos.lock_repo import LockRepo
from app.security.password import hash_password


class UserService:
    """
    Global OWNER (chủ nhà) tạo USER và gắn USER vào 1 lock ngay lập tức.
    """

    def __init__(self, db: Session):
        self.db = db
        self.accounts = AccountRepo(db)
        self.locks = LockRepo(db)
        self.members = LockMemberRepo(db)

    def create_user(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
        is_active: bool = True,
        lock_id: int,
    ):
        # 1) validate unique email
        if self.accounts.get_by_email(email):
            raise ConflictError("Email already exists")

        # 2) validate lock exists
        lock = self.locks.get(lock_id)
        if not lock:
            raise NotFoundError("Lock not found")

        # 3) create account (force USER for safety)
        acct = self.accounts.create(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            is_active=is_active,
            global_role=GlobalRole.USER,
        )
        self.db.flush()  # đảm bảo acct.id có ngay

        # 4) add membership: USER (idempotent)
        existing = self.members.get_member(lock_id=lock_id, account_id=acct.id)
        if not existing:
            self.members.add_member(
                lock_id=lock_id,
                account_id=acct.id,
                role=LockRole.USER,
            )

        self.db.commit()
        return acct

    def list_users(self, limit: int, offset: int):
        return self.accounts.list(limit=limit, offset=offset)