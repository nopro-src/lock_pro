from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db, get_ws_manager
from app.core.events import EventType

router = APIRouter()

@router.post("/heartbeat")
async def heartbeat(lock_code: str, ws=Depends(get_ws_manager)):
    # ESP32 future: send heartbeat with lock_code
    await ws.broadcast({"type": EventType.INFO, "message": "DEVICE_HEARTBEAT", "lock_code": lock_code})
    return {"ok": True}