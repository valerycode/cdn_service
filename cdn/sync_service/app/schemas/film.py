from uuid import UUID

from app.schemas.base_class import BaseSchema


class FilmBase(BaseSchema):
    """Общие свойства схем."""

    size_bytes: int


class FilmCreate(FilmBase):
    """Схема для создания."""

    id: UUID


class FilmUpdate(FilmBase):
    """Схема для обновления."""

    size_bytes: int | None = None


class Film(FilmBase):
    """Схема для возврата из API."""

    id: UUID


class FilmSync(Film):
    score: float
