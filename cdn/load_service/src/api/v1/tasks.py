from celery.result import AsyncResult
from fastapi import APIRouter

from core.core_model import CoreModel
from workers.worker import celery, load_object_to_storage

router = APIRouter()


class UploadTask(CoreModel):
    file_path: str
    object_name: str
    storage: str


class ResponseTask(CoreModel):
    task_id: str


class ResponseStatus(CoreModel):
    task_id: str
    task_status: str
    task_result: str


@router.get("/tasks/status/{task_id}", response_model=ResponseStatus)
def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery)
    return ResponseStatus(task_id=task_id, task_status=task_result.status, task_result=str(task_result.result))


@router.post("/tasks/upload_file_to_storage", response_model=ResponseTask)
def add_task_upload_to_master(task: UploadTask):
    new_task = load_object_to_storage.delay(task.file_path, task.object_name, task.storage)
    return ResponseTask(task_id=new_task.id)
