from fastapi import APIRouter

from app.api.v1 import axes, entrees, intervenants, propositions

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(entrees.router)
api_router.include_router(propositions.router)
api_router.include_router(axes.router)
api_router.include_router(intervenants.router)
