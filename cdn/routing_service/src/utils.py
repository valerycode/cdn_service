import aiohttp

from fastapi import Request

from src.config import fake
from src.settings import settings, logger


async def get_ip_address(request: Request):
    if request.client.host == "127.0.0.1":
        ip_address = fake.ipv4()
    else:
        ip_address = request.client.host
    return ip_address


async def save_info_ugc_service(film_id, user_id):
    try:
        url = f"{settings.ugc_service_url}/api/v1/record_film/{film_id}"
        data = {"user_id": user_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                response.raise_for_status()
    except aiohttp.ClientError as e:
        logger.error(f"An error occurred while sending request to UGC service: {e}")
