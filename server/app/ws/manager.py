from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict, Set, Optional

from fastapi import WebSocket
from app.schemas.ws import WsEvent


@dataclass
class ClientConn:
    ws: WebSocket
    account_id: int


class WsManager:
    """
    Production-ready-ish WS manager:
    - rooms by lock_id
    - concurrency-safe with lock
    """

    def __init__(self):
        self._rooms: Dict[int, Set[ClientConn]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket, account_id: int) -> ClientConn:
        await ws.accept()
        return ClientConn(ws=ws, account_id=account_id)

    async def join_lock_room(self, conn: ClientConn, lock_id: int) -> None:
        async with self._lock:
            self._rooms.setdefault(lock_id, set()).add(conn)

    async def leave_all(self, conn: ClientConn) -> None:
        async with self._lock:
            for lock_id in list(self._rooms.keys()):
                if conn in self._rooms[lock_id]:
                    self._rooms[lock_id].remove(conn)
                if not self._rooms[lock_id]:
                    del self._rooms[lock_id]

    async def broadcast(self, event: WsEvent) -> None:
        targets: list[ClientConn] = []
        async with self._lock:
            if event.lock_id is None:
                # broadcast global: all rooms
                for conns in self._rooms.values():
                    targets.extend(list(conns))
            else:
                targets = list(self._rooms.get(event.lock_id, set()))

        dead: list[ClientConn] = []
        for conn in targets:
            try:
                await conn.ws.send_json(event.model_dump())
            except Exception:
                dead.append(conn)

        # cleanup dead connections
        if dead:
            async with self._lock:
                for lock_id, conns in list(self._rooms.items()):
                    for d in dead:
                        conns.discard(d)
                    if not conns:
                        del self._rooms[lock_id]