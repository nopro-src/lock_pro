from __future__ import annotations

from sqlalchemy.orm import Session
from app.models.account import Account, GlobalRole


class AccountRepo:
    def __init__(self, db: Session):
        self.db = db

    def get(self, account_id: int) -> Account | None:
        return self.db.query(Account).filter(Account.id == account_id).first()

    # ✅ compatibility: old code calls get_by_id()
    def get_by_id(self, account_id: int) -> Account | None:
        return self.get(account_id)

    def get_by_email(self, email: str) -> Account | None:
        return self.db.query(Account).filter(Account.email == email).first()

    def list(self, limit: int = 100, offset: int = 0) -> list[Account]:
        return (
            self.db.query(Account)
            .order_by(Account.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(
        self,
        *,
        email: str,
        password_hash: str,
        full_name: str,
        is_active: bool = True,
        global_role: GlobalRole = GlobalRole.USER,
    ) -> Account:
        acct = Account(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            is_active=is_active,
            global_role=global_role,
        )
        self.db.add(acct)
        self.db.flush()
        return acct