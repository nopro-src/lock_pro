from __future__ import annotations

import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.logging_config import setup_logging
from app.db.session import engine
from app.db.base import Base
from app.api.routers import auth, locks, users, face, logs, system
from app.security.jwt import decode_token
from app.ws.manager import WsManager
from app.schemas.ws import WsEvent


setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger("app")

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# Create tables (prod: replace with Alembic)
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(auth.router)
app.include_router(locks.router)
app.include_router(users.router)
app.include_router(face.router)
app.include_router(logs.router)
app.include_router(system.router)

# Static admin
app.mount("/admin", StaticFiles(directory=settings.STATIC_ADMIN_DIR, html=True), name="admin")


@app.get("/")
def root():
    return RedirectResponse(url="/admin/dashboard.html")


_ws = WsManager()


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    # Auth via query param token=? OR header Authorization
    token = ws.query_params.get("token")
    if not token:
        auth = ws.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()

    if not token:
        await ws.close(code=1008)
        return

    try:
        payload = decode_token(token)
        account_id = int(payload.sub)
    except Exception:
        await ws.close(code=1008)
        return

    conn = await _ws.connect(ws, account_id=account_id)
    try:
        # first message from client should be: {"action":"join","lock_id":123}
        await ws.send_json(WsEvent(type="INFO", lock_id=None, payload={"msg": "connected"}).model_dump())
        while True:
            msg = await ws.receive_json()
            action = msg.get("action")
            if action == "join":
                lock_id = int(msg.get("lock_id"))
                await _ws.join_lock_room(conn, lock_id)
                await ws.send_json(WsEvent(type="INFO", lock_id=lock_id, payload={"msg": "joined"}).model_dump())
            else:
                await ws.send_json(WsEvent(type="ERROR", lock_id=None, payload={"msg": "unknown_action"}).model_dump())
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("ws_error", exc_info=e)
    finally:
        await _ws.leave_all(conn)