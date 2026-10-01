from fastapi import FastAPI

from pathlib import Path
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import engine
from app.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(
    title="Social Platform API",
    description="A Production-oriented social media platform.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(
    api_router,
    prefix="/api/v1",
)

Path("uploads/profiles").mkdir(parents=True, exist_ok=True)
Path("uploads/posts").mkdir(parents=True, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status" : "healthy",
        "service" : "social-platfrom-api",
        "application": settings.APP_NAME
    }
