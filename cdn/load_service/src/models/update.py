from enum import Enum

from core.core_model import CoreModel
from models.sync import MovieId

"""DTO для ответа на сервер синхронизации"""


class Actions(str, Enum):
    UPLOAD = "UPLOAD"
    DELETE = "DELETE"


class UpdateItem(CoreModel):
    action: Actions
    movie_id: MovieId


class Updates(CoreModel):
    items: list[UpdateItem]
