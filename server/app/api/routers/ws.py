from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.deps import get_ws_manager

router = APIRouter()


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket, manager=Depends(get_ws_manager)):
    await manager.connect(ws)
    try:
        while True:
            # keepalive / receive (optional)
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(ws)
    except Exception:
        await manager.disconnect(ws)