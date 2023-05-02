import logging
import os
import sys
from typing import Any

import aiohttp
from pydantic import BaseModel

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


class HTTPResponse(BaseModel):
    body: Any
    headers: dict
    status: int


async def make_get_request(path: str, params: dict = None) -> HTTPResponse:
    params = params or {}
    url = test_settings.SERVICE_API_V1_URL + path
    session = aiohttp.ClientSession()
    async with session.get(url, params=params) as response:
        resp = HTTPResponse(
            body=await response.json(),
            headers=response.headers,
            status=response.status,
        )
    await session.close()
    return resp
