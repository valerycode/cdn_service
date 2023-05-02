import logging

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1.ping import router as ping_router
from api.v1.sync import router as sync_router
from core.config import settings
from services.storage import storage

# Create a FASTAPI application
app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", default_response_class=ORJSONResponse)


@app.on_event("startup")
async def startup():
    logging.info("service start")
    logging.info("Check Redis connection")
    storage.check_broker()


app.include_router(ping_router, prefix="", tags=["Ping"])
app.include_router(sync_router, prefix="/v1", tags=["Sync"])
