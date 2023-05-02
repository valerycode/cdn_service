import logging
import os
from datetime import datetime, timedelta

from minio import Minio
from minio.error import S3Error

from config.app import app
from config.components.common import BUCKET, MINIO_ACCESS_KEY, MINIO_MASTER_STORAGE, MINIO_SECRET_KEY
from .models import Filmwork

logger = logging.getLogger(__name__)

FILE_WAS_LOADED_TO_STORAGE = 'File %s was successfully loaded to storage'
FILE_IS_DELETED = 'File %s is deleted from local folder with media files'
FILE_COULD_NOT_DE_DELETED = 'Could not delete file %s. Error occurred - %s'
ERROR_MESSAGE = 'During finding file %s in storage error occurred - %s'


@app.task
def check_status():
    films = Filmwork.objects.filter(status='waiting')
    minio = Minio(
        MINIO_MASTER_STORAGE,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    for film in films:
        try:
            minio.stat_object(BUCKET, film.file.name)
        except S3Error as error:
            logger.debug(ERROR_MESSAGE, film.file.name, error)
            if (film.created + timedelta(hours=8)).strftime('%H:%M:%S') < datetime.utcnow().strftime('%H:%M:%S'):
                film.status = 'failed'
            continue
        else:
            film.status = 'done'
            logger.debug(FILE_WAS_LOADED_TO_STORAGE, film.file.name)
            try:
                os.remove(film.file.path)
            except Exception as error:
                logger.debug(FILE_COULD_NOT_DE_DELETED, film.file.name, error)
            else:
                if not os.path.isfile(film.file.path):
                    logger.debug(FILE_IS_DELETED, film.file.name)
        finally:
            film.save()
