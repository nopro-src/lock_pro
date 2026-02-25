from __future__ import annotations

from sqlalchemy.orm import Session

from app.repos.device_repo import DeviceRepo
from app.repos.device_command_repo import DeviceCommandRepo
from app.models.device_command import CommandType


class DeviceService:
    def __init__(self, db: Session):
        self.db = db
        self.devices = DeviceRepo(db)
        self.commands = DeviceCommandRepo(db)

    def record_device_seen(self, lock_id: int, device_uid: str, fw: str = ""):
        d = self.devices.upsert_seen(lock_id, device_uid, fw=fw)
        self.db.commit()
        return d

    def create_command(self, lock_id: int, command_type: CommandType, payload: dict):
        cmd = self.commands.create(lock_id=lock_id, command_type=command_type, payload_json=payload)
        self.db.commit()
        return cmd