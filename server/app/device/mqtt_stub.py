from __future__ import annotations

import logging
from typing import Any

from app.device.transport_base import DeviceTransportBase

logger = logging.getLogger("device.mqtt_stub")


class MQTTTransportStub(DeviceTransportBase):
    """
    Stub transport: logs commands only.
    Replace later with real MQTT publish/subscribe.
    """

    def send_command(self, lock_id: int, command_type: str, payload: dict[str, Any]) -> None:
        logger.info(
            "MQTT_STUB send_command",
            extra={"lock_id": lock_id, "event_type": "LOCK_CMD"},
        )

    def broadcast_status(self) -> None:
        logger.info("MQTT_STUB broadcast_status", extra={"event_type": "DEVICE_STATUS"})