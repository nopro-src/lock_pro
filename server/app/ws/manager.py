from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Dict, Set
from fastapi import WebSocket


@dataclass
class ClientConn:
    ws: WebSocket
    account_id: int
    lock_rooms: Set[int] = field(default_factory=set)


class WsManager:
    def __init__(self) -> None:
        self._conns: Dict[int, ClientConn] = {}
        self._rooms: Dict[int, Set[int]] = {}  # lock_id -> set(account_id)
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket, account_id: int) -> ClientConn:
        await ws.accept()
        conn = ClientConn(ws=ws, account_id=account_id)
        async with self._lock:
            self._conns[account_id] = conn
        return conn

    async def join_lock_room(self, conn: ClientConn, lock_id: int) -> None:
        async with self._lock:
            conn.lock_rooms.add(lock_id)
            self._rooms.setdefault(lock_id, set()).add(conn.account_id)

    async def leave_all(self, conn: ClientConn) -> None:
        async with self._lock:
            for lock_id in list(conn.lock_rooms):
                s = self._rooms.get(lock_id)
                if s:
                    s.discard(conn.account_id)
                    if not s:
                        self._rooms.pop(lock_id, None)
            conn.lock_rooms.clear()
            cur = self._conns.get(conn.account_id)
            if cur is conn:
                self._conns.pop(conn.account_id, None)

    async def broadcast(self, event) -> None:
        payload = event.model_dump() if hasattr(event, "model_dump") else event

        async with self._lock:
            if payload.get("lock_id") is None:
                targets = list(self._conns.values())
            else:
                lock_id = int(payload["lock_id"])
                ids = list(self._rooms.get(lock_id, set()))
                targets = [self._conns[i] for i in ids if i in self._conns]

        for c in targets:
            try:
                await c.ws.send_json(payload)
            except Exception:
                pass