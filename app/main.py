from fastapi import FastAPI

from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import engine

@asynccontextmanager
async def liespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(
    title="Socail Platform API",
    description="A Production-oriented social medai platform.",
    version="0.1.0",
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status" : "healthy",
        "service" : "social-platfrom-api",
        "application": settings.APP_NAME
    }
