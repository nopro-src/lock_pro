from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models import Account


def get_by_email(db: Session, email: str) -> Account | None:
    return db.execute(select(Account).where(Account.email == email)).scalar_one_or_none()


def get_by_id(db: Session, account_id: int) -> Account | None:
    return db.get(Account, account_id)


def create(db: Session, email: str, password_hash: str, full_name: str = "") -> Account:
    acc = Account(email=email.lower().strip(), password_hash=password_hash, full_name=full_name)
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc