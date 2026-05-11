from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.projects import router as projects_router
from app.core.config import get_settings
from app.db.init_db import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)


@app.get("/", tags=["root"])
def root():
    return {
        "message": "Travel Planner API",
        "endpoints": {
            "health": "/health",
            "projects": "/projects",
            "docs": "/docs",
        },
    }


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(projects_router)
