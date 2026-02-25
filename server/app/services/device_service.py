from app.core.events import EventType


def build_lock_command(lock_id: int, action: str, ok: bool, reason: str | None = None):
    # for ESP32 later: translate to MQTT/Webhook payload
    return {
        "type": EventType.LOCK_CMD,
        "lock_id": lock_id,
        "action": action,        # OPEN / DENY / ALARM
        "ok": ok,
        "reason": reason or "",
    }