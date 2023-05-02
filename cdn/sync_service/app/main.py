from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse

from app.api.v1 import api
from app.core import logging_config  # noqa
from app.core.security import check_auth_token
from app.db.session import init_db, stop_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await stop_db()


app = FastAPI(
    docs_url="/openapi",
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    dependencies=[Depends(check_auth_token)],
)


app.include_router(api.api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
