from __future__ import annotations

import os
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.security.password import hash_password
from app.models.account import Account
from app.models.lock import Lock
from app.models.lock_member import LockMember, LockRole


def run():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # id=1 acts as system OWNER in /api/users (demo rule)
    owner = db.query(Account).filter(Account.email == "owner@example.com").first()
    if not owner:
        owner = Account(email="owner@example.com", password_hash=hash_password("Owner123456"), full_name="System Owner", is_active=True)
        db.add(owner)
        db.flush()

    admin = db.query(Account).filter(Account.email == "admin@example.com").first()
    if not admin:
        admin = Account(email="admin@example.com", password_hash=hash_password("Admin123456"), full_name="Admin", is_active=True)
        db.add(admin)
        db.flush()

    user = db.query(Account).filter(Account.email == "user@example.com").first()
    if not user:
        user = Account(email="user@example.com", password_hash=hash_password("User123456"), full_name="User", is_active=True)
        db.add(user)
        db.flush()

    lock = db.query(Lock).filter(Lock.code == "LOCK-001").first()
    if not lock:
        lock = Lock(name="Main Door", code="LOCK-001", owner_id=owner.id, threshold_override=0.70)
        db.add(lock)
        db.flush()

    def ensure_member(account_id: int, role: LockRole):
        m = db.query(LockMember).filter(LockMember.lock_id == lock.id, LockMember.account_id == account_id).first()
        if not m:
            db.add(LockMember(lock_id=lock.id, account_id=account_id, role=role))

    ensure_member(owner.id, LockRole.OWNER)
    ensure_member(admin.id, LockRole.ADMIN)
    ensure_member(user.id, LockRole.USER)

    db.commit()
    db.close()
    print("Seed done:")
    print(" owner@example.com/ Owner123456")
    print(" admin@example.com / Admin123456")
    print(" user@example.com / User123456")
    print(" Lock code: LOCK-001")


if __name__ == "__main__":
    os.environ.setdefault("DATABASE_URL", "sqlite:///./dev.db")
    run()