from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.device_command import DeviceCommand, CommandType


class DeviceCommandRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(self, lock_id: int, command_type: CommandType, payload_json: dict) -> DeviceCommand:
        cmd = DeviceCommand(lock_id=lock_id, command_type=command_type, payload_json=payload_json)
        self.db.add(cmd)
        self.db.flush()
        return cmd

    def list_pending(self, lock_id: int, limit: int = 50) -> list[DeviceCommand]:
        stmt = select(DeviceCommand).where(DeviceCommand.lock_id == lock_id, DeviceCommand.delivered_at.is_(None)).limit(limit)
        return list(self.db.execute(stmt).scalars().all())