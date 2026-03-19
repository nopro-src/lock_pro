from __future__ import annotations

from sqlalchemy.orm import Session

from app.config import settings
from app.device.mqtt_stub import MQTTTransportStub
from app.device.mqtt_transport import MQTTTransport
from app.exceptions import NotFoundError
from app.models.device_command import CommandType
from app.repos.device_command_repo import DeviceCommandRepo
from app.repos.device_repo import DeviceRepo


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

    def _get_transport(self):
        if settings.DEVICE_TRANSPORT == "mqtt":
            return MQTTTransport()
        return MQTTTransportStub()

    def send_lock_command(self, lock_id: int, command: str, extra_payload: dict | None = None):
        cmd_lower = command.strip().lower()

        if cmd_lower == "open":
            cmd_type = CommandType.OPEN
        elif cmd_lower == "close":
            cmd_type = CommandType.CLOSE
        else:
            raise ValueError(f"Unsupported command: {command}")

        device = self.devices.get_latest_by_lock_id(lock_id)
        if not device:
            raise NotFoundError("Device not found for this lock")

        payload = {
            "command": cmd_lower,
            "device_uid": device.device_uid,
        }

        if extra_payload:
            payload.update(extra_payload)

        # 1) lưu DB
        cmd = self.create_command(
            lock_id=lock_id,
            command_type=cmd_type,
            payload=payload,
        )

        # 2) publish thật
        transport = self._get_transport()
        transport.send_command(
            lock_id=lock_id,
            command_type=cmd_lower,
            payload=payload,
        )

        return cmd