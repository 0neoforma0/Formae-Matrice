from fastapi import APIRouter

from app.api.v1 import entrees, propositions

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(entrees.router)
api_router.include_router(propositions.router)
