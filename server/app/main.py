from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.routers import api_router
from app.api.routers.ws import router as ws_router  # <-- add
from app.db import Base, engine
from app.db.seed import seed_default_owner


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # init db
    Base.metadata.create_all(bind=engine)
    seed_default_owner()

    # API under /api
    app.include_router(api_router, prefix="/api")

    # WebSocket should NOT be under /api (so path is /ws)
    app.include_router(ws_router)

    # Serve web-admin under /admin (avoid catching /ws)
    app.mount("/admin", StaticFiles(directory="../web-admin/public", html=True), name="web-admin")

    return app


app = create_app()