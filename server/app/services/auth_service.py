from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from app.repos.account_repo import AccountRepo
from app.security.password import hash_password, verify_password
from app.security.jwt import create_access_token
from app.exceptions import ConflictError, ForbiddenError

# NEW: GlobalRole
from app.models.account import GlobalRole


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.accounts = AccountRepo(db)

    def register(self, email: str, password: str, full_name: str):
        if self.accounts.get_by_email(email):
            raise ConflictError("Email already exists")
        acct = self.accounts.create(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            global_role=GlobalRole.USER,  # default
        )
        self.db.commit()
        return acct

    def login(self, email: str, password: str) -> tuple[str, str]:
        acct = self.accounts.get_by_email(email)
        if not acct:
            raise ForbiddenError("Invalid credentials")
        if not acct.is_active:
            raise ForbiddenError("Account disabled")
        if not verify_password(password, acct.password_hash):
            raise ForbiddenError("Invalid credentials")

        acct.last_login_at = datetime.utcnow()
        self.db.commit()

        token = create_access_token(acct.id)
        return token, str(acct.global_role.value if hasattr(acct.global_role, "value") else acct.global_role)