import httpx
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.config import settings
from app.services.sync import prepare_synchronization

router = APIRouter()


@router.post("")
async def sync(storage_id: str, session: AsyncSession = Depends(deps.get_session)):
    sync_task, storage = await prepare_synchronization(session, storage_id)
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{storage.url}{settings.SYNC_HTTP_PATH}",
            json=jsonable_encoder(sync_task),
            headers={"Authorization": settings.SECRET_KEY},
        )
