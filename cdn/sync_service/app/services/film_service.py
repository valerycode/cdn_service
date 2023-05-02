from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Film, S3Storage, films_s3storages
from app.schemas import FilmCreate, FilmUpdate
from app.services.crud_base import CRUDBase


class FilmService(CRUDBase[Film, FilmCreate, FilmUpdate]):
    async def add_film_to_storage(
        self,
        session: AsyncSession,
        film_id: UUID,
        storage: S3Storage,
        film_size_bytes: int | None = None,
    ) -> Film | None:
        result = await session.execute(
            select(self.model).filter(self.model.id == film_id).options(selectinload(self.model.storages))
        )
        film = result.scalar_one_or_none()
        if not film and film_size_bytes:
            # добавляем новый фильм
            film = self.model(id=film_id, size_bytes=film_size_bytes, storages=[storage])
            session.add(film)
        elif not film and film_size_bytes is None:
            # для нового фильма обязательно нужен размер
            return None
        else:
            # добавляем существующий фильм в хранилище
            film.storages.append(storage)

        await session.commit()
        return film

    async def delete_film_from_storage(
        self,
        session: AsyncSession,
        film_id: UUID,
        storage: S3Storage,
    ) -> Film | None:
        result = await session.execute(
            select(self.model).filter(self.model.id == film_id).options(selectinload(self.model.storages))
        )
        film = result.scalar_one()
        film.storages.remove(storage)
        await session.commit()
        return film

    async def get_films_by_storage(self, session: AsyncSession, storage_id: str):
        result = await session.execute(
            select(self.model).join(films_s3storages).filter(films_s3storages.c.storage_id == storage_id)
        )
        return result.scalars().all()


film_service = FilmService(Film)
