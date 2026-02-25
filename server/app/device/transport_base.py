from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DeviceTransportBase(ABC):
    @abstractmethod
    def send_command(self, lock_id: int, command_type: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def broadcast_status(self) -> None:
        raise NotImplementedError