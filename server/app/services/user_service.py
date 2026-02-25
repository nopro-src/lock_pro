from __future__ import annotations

from sqlalchemy.orm import Session

from app.repos.account_repo import AccountRepo
from app.security.password import hash_password
from app.exceptions import ConflictError


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.accounts = AccountRepo(db)

    def create_user(self, email: str, password: str, full_name: str, is_active: bool):
        if self.accounts.get_by_email(email):
            raise ConflictError("Email already exists")
        acct = self.accounts.create(email=email, password_hash=hash_password(password), full_name=full_name, is_active=is_active)
        self.db.commit()
        return acct

    def list_users(self, limit: int = 100, offset: int = 0):
        return self.accounts.list(limit=limit, offset=offset)