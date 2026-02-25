from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.device import Device, DeviceStatus


class DeviceRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_uid(self, lock_id: int, device_uid: str) -> Device | None:
        stmt = select(Device).where(Device.lock_id == lock_id, Device.device_uid == device_uid)
        return self.db.execute(stmt).scalars().first()

    def upsert_seen(self, lock_id: int, device_uid: str, fw: str = "") -> Device:
        d = self.get_by_uid(lock_id, device_uid)
        now = datetime.utcnow()
        if d:
            d.last_seen_at = now
            d.status = DeviceStatus.ONLINE
            if fw:
                d.firmware_version = fw
            self.db.flush()
            return d
        d = Device(lock_id=lock_id, device_uid=device_uid, firmware_version=fw, status=DeviceStatus.ONLINE, last_seen_at=now)
        self.db.add(d)
        self.db.flush()
        return d