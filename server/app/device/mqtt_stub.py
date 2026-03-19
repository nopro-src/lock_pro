from __future__ import annotations

import logging
from typing import Any

from app.device.transport_base import DeviceTransportBase

logger = logging.getLogger("device.mqtt_stub")


class MQTTTransportStub(DeviceTransportBase):
    """
    Stub transport: logs commands only.
    """

    def send_command(self, lock_id: int, command_type: str, payload: dict[str, Any]) -> None:
        logger.info(
            "[MQTT_STUB] send_command lock_id=%s command_type=%s payload=%s",
            lock_id,
            command_type,
            payload,
            extra={"lock_id": lock_id, "event_type": "LOCK_CMD"},
        )

    def broadcast_status(self) -> None:
        logger.info("[MQTT_STUB] broadcast_status", extra={"event_type": "DEVICE_STATUS"})