from http import HTTPStatus

import pytest
import pytest_asyncio
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.core.config import settings
from app.db.session import add_storages
from app.models.models import S3Storage
from app.services.s3storage_service import s3storage_service

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def clear_s3storage_table(session: AsyncSession):
    await session.execute(delete(S3Storage))
    await session.commit()


async def test_create_storage(client: AsyncClient):
    storage = schemas.S3StorageCreate(
        id="test", url="http://test.com", ip_address="111.111.111.111", size_bytes=2**50
    )
    response = await client.post(
        "api/v1/storages",
        json=jsonable_encoder(storage),
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": "test",
        "url": "http://test.com",
        "ip_address": "111.111.111.111",
        "size_bytes": 2**50,
    }
    assert response.json()["url"] == "http://test.com"
    assert response.json()["ip_address"] == "111.111.111.111"
    assert response.json()["size_bytes"] == 2**50


async def test_read_multiple_storages(client: AsyncClient, clear_s3storage_table):
    storage = schemas.S3StorageCreate(
        id="test1", url="http://test1.com", ip_address="111.111.111.111", size_bytes=2**50
    )
    await client.post(
        "api/v1/storages",
        json=jsonable_encoder(storage),
    )
    storage = schemas.S3StorageCreate(
        id="test2", url="http://test2.com", ip_address="222.222.222.222", size_bytes=2**50
    )
    await client.post(
        "api/v1/storages",
        json=jsonable_encoder(storage),
    )
    response = await client.get("api/v1/storages")
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 2


async def test_read_storage(client: AsyncClient, clear_s3storage_table):
    storage = schemas.S3StorageCreate(
        id="test", url="http://test.com", ip_address="111.111.111.111", size_bytes=2**50
    )
    response = await client.post(
        "api/v1/storages",
        json=jsonable_encoder(storage),
    )
    storage_id = response.json()["id"]
    response = await client.get(f"api/v1/storages/{storage_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["url"] == "http://test.com"


async def test_update_storage(client: AsyncClient, clear_s3storage_table):
    storage = schemas.S3StorageCreate(
        id="test", url="http://test.com", ip_address="111.111.111.111", size_bytes=2**50
    )
    response = await client.post(
        "api/v1/storages",
        json=jsonable_encoder(storage),
    )
    storage_id = response.json()["id"]
    updated_storage = schemas.S3StorageUpdate(
        url="http://updated.com", ip_address="111.111.111.111", size_bytes=2**50
    )
    response = await client.patch(
        f"api/v1/storages/{storage_id}",
        json=jsonable_encoder(updated_storage),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["url"] == "http://updated.com"
    assert response.json()["ip_address"] == "111.111.111.111"


async def test_delete_storage(client: AsyncClient, clear_s3storage_table):
    storage = schemas.S3StorageCreate(
        id="test", url="http://test.com", ip_address="111.111.111.111", size_bytes=2**50
    )
    response = await client.post(
        "api/v1/storages",
        json=jsonable_encoder(storage),
    )
    storage_id = response.json()["id"]
    response = await client.delete(f"api/v1/storages/{storage_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == storage_id


async def test_get_master_storage(session: AsyncSession):
    await add_storages(session)
    master = await s3storage_service.get_master_storage(session)
    assert master.url == settings.S3_SETTINGS[0].url


async def test_get_storage_by_ip(session: AsyncSession):
    storage_ip = settings.S3_SETTINGS[-1].ip
    await add_storages(session)
    storage = await s3storage_service.get_storage_by_ip(session, storage_ip)
    assert storage.ip_address == storage_ip
