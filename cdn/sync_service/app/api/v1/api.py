from fastapi import APIRouter

from app.api.v1 import films, s3storages, sync

api_router = APIRouter()
api_router.include_router(films.router, prefix="/films", tags=["films"])
api_router.include_router(s3storages.router, prefix="/storages", tags=["storages"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
