from pydantic import BaseModel


class Storage(BaseModel):
    url: str
    ip: str
    access_key: str
    secret_key: str
