from __future__ import annotations

import logging
import ssl
from typing import Any

import paho.mqtt.client as mqtt

from app.config import settings
from app.device.transport_base import DeviceTransportBase

logger = logging.getLogger("device.mqtt")


class MQTTTransport(DeviceTransportBase):
    def __init__(self):
        self.host = settings.MQTT_HOST
        self.port = settings.MQTT_PORT
        self.username = settings.MQTT_USERNAME
        self.password = settings.MQTT_PASSWORD
        self.topic_prefix = settings.MQTT_TOPIC_PREFIX.rstrip("/")

    def _build_client(self) -> mqtt.Client:
        client = mqtt.Client(client_id=settings.MQTT_BACKEND_CLIENT_ID, protocol=mqtt.MQTTv311)

        if self.username:
            client.username_pw_set(self.username, self.password)

        if settings.MQTT_USE_TLS:
            client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
            client.tls_insecure_set(False)

        return client

    def send_command(self, lock_id: int, command_type: str, payload: dict[str, Any]) -> None:
        device_uid = payload.get("device_uid")
        command = payload.get("command", command_type)

        if not device_uid:
            raise ValueError("payload.device_uid is required")

        topic = f"{self.topic_prefix}/{device_uid}/command"

        client = self._build_client()
        try:
            client.connect(self.host, self.port, keepalive=30)
            result = client.publish(topic, command, qos=1, retain=False)
            result.wait_for_publish()

            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"MQTT publish failed with rc={result.rc}")

            logger.info(
                "[MQTT] published lock_id=%s topic=%s payload=%s",
                lock_id,
                topic,
                command,
                extra={"lock_id": lock_id, "event_type": "LOCK_CMD"},
            )
        finally:
            try:
                client.disconnect()
            except Exception:
                pass

    def broadcast_status(self) -> None:
        logger.info("[MQTT] broadcast_status noop", extra={"event_type": "DEVICE_STATUS"})