from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

router = APIRouter()


@router.get("/ping")
async def ping():
    return ORJSONResponse("pong")
