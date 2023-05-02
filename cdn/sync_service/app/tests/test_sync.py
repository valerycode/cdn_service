from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import add_storages
from app.schemas import Film, FilmSync, Movie, SyncTask, UploadTask
from app.services.sync import make_sync_task

pytestmark = pytest.mark.asyncio


async def test_make_sync_task(session: AsyncSession):
    await add_storages(session)
    stored_films = [
        Film(id="507447e5-1d3a-4e1e-b16a-3868dbc6cf90", size_bytes=100),
        Film(id="507447e5-1d3a-4e1e-b16a-3868dbc6cf91", size_bytes=100),
    ]
    scored_films = [
        FilmSync(id="507447e5-1d3a-4e1e-b16a-3868dbc6cf90", size_bytes=100, score=0.1),
        FilmSync(id="507447e5-1d3a-4e1e-b16a-3868dbc6cf91", size_bytes=100, score=0.9),
        FilmSync(id="507447e5-1d3a-4e1e-b16a-3868dbc6cf92", size_bytes=100, score=0.8),
    ]
    result = await make_sync_task(session, scored_films, stored_films, 300, 50)
    sync_task = SyncTask(
        delete=[Movie(movie_id=UUID("507447e5-1d3a-4e1e-b16a-3868dbc6cf90"))],
        upload=[
            UploadTask(movie_id=UUID("507447e5-1d3a-4e1e-b16a-3868dbc6cf92"), storage_url=settings.S3_SETTINGS[0].url)
        ],
    )
    assert result == sync_task
