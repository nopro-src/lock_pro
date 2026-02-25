from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.account import Account


class AccountRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, account_id: int) -> Account | None:
        return self.db.get(Account, account_id)

    def get_by_email(self, email: str) -> Account | None:
        stmt = select(Account).where(Account.email == email)
        return self.db.execute(stmt).scalars().first()

    def create(self, email: str, password_hash: str, full_name: str, is_active: bool = True) -> Account:
        acct = Account(email=email, password_hash=password_hash, full_name=full_name, is_active=is_active)
        self.db.add(acct)
        self.db.flush()
        return acct

    def list(self, limit: int = 100, offset: int = 0) -> list[Account]:
        stmt = select(Account).order_by(Account.id.desc()).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())