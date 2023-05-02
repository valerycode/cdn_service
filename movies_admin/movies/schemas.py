import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseModelMixin(BaseModel):

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class UploadTask(BaseModelMixin):
    file_path: str
    object_name: str
    storage: str
