from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from core.config import settings

API_KEY_NAME = "Authorization"
API_KEY = settings.API_KEY
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# usage: async def get_open_api_endpoint(api_key: APIKey = Depends(get_api_key)):


async def get_api_key(key_header: str = Security(api_key_header)):
    if key_header == API_KEY or key_header == f'Bearer {API_KEY}':
        return key_header
    else:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")


def get_api_key_header():
    return {API_KEY_NAME: API_KEY}
