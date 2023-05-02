from celery import Celery
from celery.utils.log import get_task_logger

from core.config import settings
from models.sync import SyncTask
from models.update import Actions, UpdateItem
from services.s3 import copy_file, delete_file, load_file_to_storage
from services.storage import storage
from services.update import do_update, send_heartbeat

#   Celery
celery = Celery("tasks", broker=settings.CELERY_BROKER_URI, backend=settings.CELERY_BACKEND_URI)

celery.conf.beat_schedule = {
    "add-every-30-seconds": {
        "task": "Sync",
        "schedule": settings.BEAT_TIMEOUT,
    },
}

# Create a logger - Enable to display the message on the task logger
celery_log = get_task_logger(__name__)


class TaskFailure(Exception):
    pass


def add_result_notice(action: Actions, file_name: str):
    """Добавить уведомление на отправку"""
    storage.add_update(UpdateItem(action=action, movie_id=file_name))
    celery_log.debug("add result notice ({0},{1})".format(action, file_name))


@celery.task(name="MinioUpload", autoretry_for=(TaskFailure,), retry_kwargs={"max_retries": 5, "retry_backoff": True})
def load_object(file_name: str, source: str) -> dict[str, str]:
    result = copy_file(file_name, source, settings.HOME_STORAGE_URI)

    if "error" in result:
        raise TaskFailure(result)

    add_result_notice(Actions.UPLOAD, file_name)
    return result


@celery.task(name="MinioDelete")
def delete_object(file_name: str) -> dict[str, str]:
    result = delete_file(file_name, settings.HOME_STORAGE_URI)

    if "error" in result:
        raise TaskFailure(result)

    add_result_notice(Actions.DELETE, file_name)
    return result


@celery.task(name="Sync")
def do_sync():
    res_hb = send_heartbeat()
    res_upd = do_update()
    return {"heartbeat": res_hb, "update": res_upd}


def add_tasks(tasks_list: SyncTask):
    """Добавляем в Celery задачи из списка задач"""

    if tasks_list.delete:
        for task in tasks_list.delete:
            delete_object.delay(task.movie_id)

    if tasks_list.upload:
        for task in tasks_list.upload:
            load_object.delay(task.movie_id, task.storage_url)

    return


@celery.task(name="UploadFileToStorage")
def load_object_to_storage(file_path: str, object_name: str, storage: str):
    result = load_file_to_storage(file_path, object_name, storage)

    if "error" in result:
        raise TaskFailure(result)

    return result
