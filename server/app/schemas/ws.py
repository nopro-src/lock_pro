from __future__ import annotations

from pydantic import BaseModel
from typing import Any, Literal


WsEventType = Literal["ENROLL", "VERIFY", "LOCK_CMD", "DEVICE_STATUS", "ERROR", "INFO"]


class WsEvent(BaseModel):
    type: WsEventType
    lock_id: int | None = None
    payload: dict[str, Any] = {}