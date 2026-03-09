from __future__ import annotations

import logging
from pathlib import Path

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

Base.metadata.create_all(bind=engine)

# Single WS manager
app.state.ws_manager = WsManager()

# Routers
app.include_router(auth.router)
app.include_router(locks.router)
app.include_router(users.router)
app.include_router(face.router)
app.include_router(logs.router)
app.include_router(system.router)

# -----------------------------
# Static UI directories
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]   # smart-lock-face-pro/
WEB_DIR = BASE_DIR / "web"
OWNER_DIR = WEB_DIR / "owner"
USER_DIR = WEB_DIR / "user"

print("MAIN FILE =", __file__)
print("BASE_DIR  =", BASE_DIR)
print("WEB_DIR   =", WEB_DIR)
print("OWNER_DIR =", OWNER_DIR)
print("USER_DIR  =", USER_DIR)
print("OWNER DIR EXISTS =", OWNER_DIR.exists())
print("USER DIR EXISTS  =", USER_DIR.exists())
print("OWNER CSS EXISTS =", (OWNER_DIR / "assets" / "styles.css").exists())
print("USER CSS EXISTS  =", (USER_DIR / "assets" / "styles.css").exists())

# Mount static UIs directly from /web
app.mount("/owner", StaticFiles(directory=str(OWNER_DIR), html=True), name="owner")
app.mount("/user", StaticFiles(directory=str(USER_DIR), html=True), name="user")


@app.get("/")
def root():
    return RedirectResponse(url="/owner/login.html")


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    token = ws.query_params.get("token")
    if not token:
        auth_header = ws.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()

    if not token:
        await ws.close(code=1008)
        return

    try:
        payload = decode_token(token)
        account_id = int(payload.sub)
    except Exception:
        await ws.close(code=1008)
        return

    ws_manager: WsManager = app.state.ws_manager
    conn = await ws_manager.connect(ws, account_id=account_id)

    try:
        await ws.send_json(
            WsEvent(
                type="INFO",
                lock_id=None,
                payload={"msg": "connected"}
            ).model_dump()
        )

        while True:
            msg = await ws.receive_json()

            if msg.get("action") == "join":
                try:
                    lock_id = int(msg.get("lock_id"))
                except Exception:
                    await ws.send_json(
                        WsEvent(
                            type="ERROR",
                            lock_id=None,
                            payload={"msg": "invalid_lock_id"}
                        ).model_dump()
                    )
                    continue

                await ws_manager.join_lock_room(conn, lock_id)
                await ws.send_json(
                    WsEvent(
                        type="INFO",
                        lock_id=lock_id,
                        payload={"msg": "joined"}
                    ).model_dump()
                )
            else:
                await ws.send_json(
                    WsEvent(
                        type="ERROR",
                        lock_id=None,
                        payload={"msg": "unknown_action"}
                    ).model_dump()
                )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.exception("ws_error: %s", e)
    finally:
        await ws_manager.leave_all(conn)