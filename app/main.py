from fastapi import FastAPI

app = FastAPI(
    title="Socail Platform API",
    description="A Production-oriented social medai platform.",
    version="0.1.0",
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status" : "healthy",
        "service" : "social-platfrom-api"
    }
