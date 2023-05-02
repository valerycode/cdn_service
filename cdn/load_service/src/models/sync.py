from pydantic import AnyUrl

from core.core_model import CoreModel

"""DTO для sync API"""

MovieId = str


class Movie(CoreModel):
    movie_id: MovieId


class UploadTask(CoreModel):
    movie_id: MovieId
    storage_url: AnyUrl


class SyncTask(CoreModel):
    delete: list[Movie] | None
    upload: list[UploadTask] | None
