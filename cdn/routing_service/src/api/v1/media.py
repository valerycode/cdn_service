from uuid import UUID

from fastapi import Depends, HTTPException, APIRouter
from fastapi import Request

from src.config import get_storage_worker
from src.jwt_config import AccessTokenPayload, jwt_bearer
from src.utils import save_info_ugc_service, get_ip_address

router = APIRouter(prefix="/media", tags=["media"], responses={404: {"description": "Not found"}})


@router.get("/get_media/{obj_name}")
async def get_media(
        request: Request,
        obj_name: UUID,
        token_payload: AccessTokenPayload = Depends(jwt_bearer),
):
    user_id = str(token_payload.sub)
    storage_worker = await get_storage_worker()
    await save_info_ugc_service(obj_name, user_id)
    ip_address = await get_ip_address(request)
    storages = await storage_worker.get_storages(ip_address)
    if not storages:
        return HTTPException(status_code=404, detail="storages not found")
    for storage_info in storages:
        storage = storage_info.get("storage")
        if not storage:
            continue
        if storage.check_file(obj_name):
            url = storage.get_link_file(obj_name)
            return {"url": url}
    return HTTPException(status_code=404, detail="file not found")
