from fastapi import APIRouter, Body, Depends

from core.api_key import get_api_key
from models.sync import SyncTask
from workers.worker import add_tasks

router = APIRouter()


@router.post("/tasks/sync")
def add_sync(task: SyncTask = Body(...), api_key=Depends(get_api_key)):
    add_tasks(task)

    # если дошли сюда - все ОК
    return {"result": "OK"}
