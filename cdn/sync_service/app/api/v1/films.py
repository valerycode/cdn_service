from http import HTTPStatus
from urllib.parse import urlparse
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api import deps
from app.services.film_service import film_service
from app.services.s3storage_service import s3storage_service

router = APIRouter()


@router.post("/events", status_code=HTTPStatus.OK)
async def process_s3_event(
    request: Request,
    session: AsyncSession = Depends(deps.get_session),
):
    event = await request.json()
    for record in event["Records"]:
        film_id = record["s3"]["object"]["key"]
        storage_url = record['responseElements']['x-minio-origin-endpoint']
        storage_ip = urlparse(storage_url).netloc.split(":")[0]
        event_type = record["eventName"]

        storage = await s3storage_service.get_storage_by_ip(session, storage_ip)
        if not storage:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Storage ip {storage_ip} not found")

        if event_type.startswith("s3:ObjectCreated"):
            film_size = record["s3"]["object"]["size"]
            await film_service.add_film_to_storage(session, film_id, storage, film_size)
        if event_type.startswith("s3:ObjectRemoved"):
            await film_service.delete_film_from_storage(session, film_id, storage)


@router.get("/{film_id}/storages", response_model=list[schemas.S3Storage])
async def read_film_storages(film_id: UUID, session: AsyncSession = Depends(deps.get_session)):
    s3storages = await s3storage_service.read_multi_by_film(session, film_id)
    return s3storages


@router.post("", response_model=schemas.Film, status_code=HTTPStatus.CREATED)
async def create_film(
    film_in: schemas.FilmCreate,
    session: AsyncSession = Depends(deps.get_session),
):
    film = await film_service.create(session, obj_in=film_in)
    return film


@router.delete("/{film_id}")
async def delete_film(
    film_id: UUID,
    session: AsyncSession = Depends(deps.get_session),
):
    film = await film_service.delete(session, id=film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Film not found")
    return film
