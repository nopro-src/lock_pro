from __future__ import annotations

import os
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.security.password import hash_password
from app.models.account import Account, GlobalRole
from app.models.lock import Lock
from app.models.lock_member import LockMember, LockRole
from app.models.device import Device, DeviceStatus


def run():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    owner = db.query(Account).filter(Account.email == "owner@example.com").first()
    if not owner:
        owner = Account(
            email="owner@example.com",
            password_hash=hash_password("Owner123456"),
            full_name="Home Owner",
            is_active=True,
            global_role=GlobalRole.OWNER,
        )
        db.add(owner)
        db.flush()

    user = db.query(Account).filter(Account.email == "user@example.com").first()
    if not user:
        user = Account(
            email="user@example.com",
            password_hash=hash_password("User123456"),
            full_name="User",
            is_active=True,
            global_role=GlobalRole.USER,
        )
        db.add(user)
        db.flush()

    lock = db.query(Lock).filter(Lock.code == "LOCK-001").first()
    if not lock:
        lock = Lock(
            name="Main Door",
            code="LOCK-001",
            owner_id=owner.id,
            threshold_override=0.70,
        )
        db.add(lock)
        db.flush()

    def ensure_member(account_id: int, role: LockRole):
        m = db.query(LockMember).filter(
            LockMember.lock_id == lock.id,
            LockMember.account_id == account_id
        ).first()
        if not m:
            db.add(LockMember(lock_id=lock.id, account_id=account_id, role=role))

    ensure_member(owner.id, LockRole.OWNER)
    ensure_member(user.id, LockRole.USER)

    # Tạo device map với ESP32
    device = db.query(Device).filter(
        Device.lock_id == lock.id,
        Device.device_uid == "lock_001"
    ).first()

    if not device:
        device = Device(
            lock_id=lock.id,
            device_uid="lock_001",
            firmware_version="esp32-v1",
            status=DeviceStatus.ONLINE,
            last_seen_at=None,
        )
        db.add(device)

    db.commit()
    db.close()

    print("Seed done:")
    print(" owner@example.com / Owner123456 (global_role=OWNER)")
    print(" user@example.com  / User123456  (global_role=USER)")
    print(" Lock code: LOCK-001")
    print(" Device UID: lock_001")


if __name__ == "__main__":
    os.environ.setdefault("DATABASE_URL", "sqlite:///./dev.db")
    run()