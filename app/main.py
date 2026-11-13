
from fastapi import FastAPI

from app.api.v1.documents import router as documents_router

app = FastAPI(
    title="Palm Mind RAG API",
    description="Document-based conversational RAG backend",
    version="1.0.0",
)

app.include_router(
    documents_router,
    prefix="/api/v1",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "application": "Palm Mind RAG API",
    }
