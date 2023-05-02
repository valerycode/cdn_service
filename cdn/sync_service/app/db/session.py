import logging
import socket

import asyncpg
import backoff
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base_class import Base

# нужно импортировать модели, чтобы алхимия знала о них
from app.models.models import Film, S3Storage, films_s3storages  # noqa

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=settings.DEBUG)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

logger = logging.getLogger(__name__)


@backoff.on_exception(
    backoff.expo,
    exception=(ConnectionRefusedError, asyncpg.CannotConnectNowError, socket.gaierror),
    max_time=60,
    max_value=5,
)
async def check_connection():
    async with engine.connect():
        pass


@backoff.on_exception(  # ждем создание таблицы
    backoff.expo,
    exception=ProgrammingError,
    max_time=60,
    max_value=5,
)
async def add_storages(session: AsyncSession):
    for s3_settings in settings.S3_SETTINGS:
        storage = S3Storage(
            id=s3_settings.id, url=s3_settings.url, ip_address=s3_settings.ip, size_bytes=s3_settings.size
        )
        session.add(storage)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
        except ProgrammingError:
            await session.rollback()
            raise


async def recreate_tables(session: AsyncSession):
    conn = await session.connection()
    await conn.run_sync(Base.metadata.drop_all)
    await conn.run_sync(Base.metadata.create_all)
    await session.commit()


async def init_db():
    await check_connection()
    async with async_session() as session:
        # добавляем хранилища в базу
        await add_storages(session)


async def stop_db():
    await engine.dispose()
