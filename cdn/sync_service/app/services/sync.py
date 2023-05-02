import random
from operator import attrgetter
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.models import S3Storage
from app.schemas import Film, FilmSync, Movie, SyncTask, UploadTask
from app.services.film_service import film_service
from app.services.s3storage_service import s3storage_service


async def get_films_score(session: AsyncSession) -> list[FilmSync]:
    # предполагаем, что есть сервис аналитики, который дает прогноз по
    # популярности фильмов, сейчас берем случайные значения популярности
    films = await film_service.read_multi(session)
    films = [FilmSync(id=film.id, size_bytes=film.size_bytes, score=random.random()) for film in films]
    return films


async def select_storages(session: AsyncSession, film_ids: list[UUID]) -> list[S3Storage]:
    # можно сделать алгоритм откуда загружать каждый фильм с учетом
    # расстояния и загруженности хранилищ, сейчас возвращаем мастер
    # для всех фильмов
    return [await s3storage_service.get_master_storage(session)] * len(film_ids)


async def make_sync_task(
    session: AsyncSession,
    film_scores: list[FilmSync],
    stored_films: list[Film],
    storage_size: int,
    free_space_limit: int,
) -> SyncTask:
    film_scores.sort(key=attrgetter("score"), reverse=True)
    film_ids_to_store = set()
    free_space = storage_size
    for film in film_scores:
        free_space -= film.size_bytes
        if free_space < free_space_limit:
            break
        film_ids_to_store.add(film.id)

    stored_film_ids = {film.id for film in stored_films}

    film_ids_to_upload = list(film_ids_to_store - stored_film_ids)
    film_ids_to_delete = list(stored_film_ids - film_ids_to_store)

    to_delete = [Movie(movie_id=film_id) for film_id in film_ids_to_delete]
    storages_to_download_from = await select_storages(session, film_ids_to_upload)
    to_upload = []
    for film_id, storage in zip(film_ids_to_upload, storages_to_download_from):
        to_upload.append(UploadTask(movie_id=film_id, storage_url=storage.url))
    return SyncTask(delete=to_delete, upload=to_upload)


async def prepare_synchronization(session: AsyncSession, storage_id: str):
    films_with_scores = await get_films_score(session)
    storage = await s3storage_service.read(session, id=storage_id)
    films_in_storage = await film_service.get_films_by_storage(session, storage.id)

    task = await make_sync_task(
        session, films_with_scores, films_in_storage, storage.size_bytes, settings.S3_FREE_SPACE_LIMIT
    )

    await s3storage_service.delete_films_from_storage(session, storage_id, [movie.movie_id for movie in task.delete])

    return task, storage
