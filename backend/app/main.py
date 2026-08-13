from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="Matrice",
    description="La mémoire vivante du projet — Formae.",
    version="0.1.0",
)

app.include_router(api_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "environment": settings.environment}
