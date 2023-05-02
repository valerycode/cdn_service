from typing import Any, Dict, Generic, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_class import Base
from app.schemas.base_class import BaseSchema

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def create(self, session: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def read(self, session: AsyncSession, id: Any) -> ModelType | None:
        result = await session.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()

    async def read_multi(self, session: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await session.scalars(select(self.model).offset(skip).limit(limit))
        return result.all()

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = jsonable_encoder(obj_in)
        else:
            update_data = jsonable_encoder(obj_in.dict(exclude_unset=True))
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        return db_obj

    async def delete(self, session: AsyncSession, *, id: int) -> ModelType | None:
        result = await session.execute(select(self.model).filter(self.model.id == id))
        db_obj = result.scalar_one_or_none()
        await session.delete(db_obj)
        await session.commit()
        return db_obj
