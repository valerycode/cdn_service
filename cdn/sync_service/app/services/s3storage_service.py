from uuid import UUID

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.models import S3Storage, films_s3storages
from app.schemas import S3StorageCreate, S3StorageUpdate
from app.services.crud_base import CRUDBase


class S3StorageService(CRUDBase[S3Storage, S3StorageCreate, S3StorageUpdate]):
    async def read_multi_by_film(self, session: AsyncSession, film_id: UUID) -> list[S3Storage]:
        result = await session.execute(
            select(self.model).join(films_s3storages).filter(films_s3storages.c.film_id == film_id)
        )
        return result.scalars().all()

    async def get_master_storage(self, session: AsyncSession) -> S3Storage:
        result = await session.execute(select(self.model).filter(self.model.id == settings.S3_MASTER_ID))
        return result.scalars().one()

    async def get_storage_by_ip(self, session: AsyncSession, storage_ip: str) -> S3Storage | None:
        result = await session.execute(select(self.model).filter(self.model.ip_address == storage_ip))
        return result.scalar_one_or_none()

    async def delete_films_from_storage(self, session: AsyncSession, storage_id: str, film_ids: list[UUID]):
        await session.execute(
            delete(films_s3storages).where(
                and_(films_s3storages.c.storage_id == storage_id, films_s3storages.c.film_id.in_(film_ids))
            )
        )


s3storage_service = S3StorageService(S3Storage)
