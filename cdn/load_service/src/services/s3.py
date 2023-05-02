import logging

from minio import Minio
from minio.error import S3Error
from urllib3.exceptions import HTTPError

from core.config import settings

"""Обертка над Minio для копирования и удаления"""

PART_SIZE = 10 * 1024 * 1024
PARALLEL_UPLOADS = 4


class LoaderException(Exception):
    pass


class MinioLoader:
    source_minio: Minio
    destination_minio: Minio
    part_size = 10 * 1024 * 1024  # для загрузки больших файлов по частям
    parallel_uploads = 4

    def __init__(self, source_host: str, destination_host: str, access_key: str, secret_key: str):
        def split_host_uri(host: str) -> tuple[bool, str]:
            """
            выделяет из URL хост и схему
            Так как Минио вместе со схемой не понимает путь
            """
            lst = host.split("://")
            secure = (len(lst) == 2) and (lst[0] == "https")
            return secure, lst[-1]

        secure, host = split_host_uri(source_host)
        self.source_minio = Minio(host, access_key=access_key, secret_key=secret_key, secure=secure)

        secure, host = split_host_uri(destination_host)
        self.destination_minio = Minio(host, access_key=access_key, secret_key=secret_key, secure=secure)

    def copy_file(
        self, source_bucket: str, source_object: str, destination_bucket: str, destination_object: str
    ) -> dict:
        # 1 Получаем объект
        try:
            response = self.source_minio.get_object(source_bucket, source_object)
            size = int(response.info()["Content-Length"])
        except (S3Error, HTTPError) as err:
            logging.error(err)
            raise LoaderException(err)

        try:
            # 2 создаем bucket если его нет
            found = self.destination_minio.bucket_exists(destination_bucket)
            if not found:
                self.destination_minio.make_bucket(destination_bucket)
                logging.debug("Create new bucket: [{0}]".format(destination_bucket))

            # 3 Копируем данные
            result = self.destination_minio.put_object(
                destination_bucket,
                destination_object,
                data=response,
                length=size,
                num_parallel_uploads=self.parallel_uploads,
                part_size=self.part_size,
            )

        except HTTPError as err:
            logging.error(err)
            raise LoaderException(err)

        finally:
            response.close()
            response.release_conn()

        logging.debug(
            "created {0} object; etag: {1}, version-id: {2}".format(result.object_name, result.etag, result.version_id)
        )
        return {"name": result.object_name, "etag": result.etag, "size": size}

    def check_source(self) -> bool:
        try:
            self.source_minio.bucket_exists("movies")
        except HTTPError:
            return False

        return True

    def check_destination(self) -> bool:
        try:
            self.destination_minio.bucket_exists("movies")
        except HTTPError:
            return False

        return True


def copy_file(file_name: str, source: str, destination: str) -> dict[str, str]:
    loader = MinioLoader(source, destination, settings.ACCESS_KEY, settings.SECRET_KEY)
    if not loader.check_source():
        return {"error": "source check error"}

    if not loader.check_destination():
        return {"error": "destination check error"}

    try:
        result = loader.copy_file(settings.BUCKET, file_name, settings.BUCKET, file_name)

    except LoaderException as err:
        return {"error": str(err)}

    return result


def delete_file(file_name: str, storage: str) -> dict[str, str]:
    minio = Minio(storage, access_key=settings.ACCESS_KEY, secret_key=settings.SECRET_KEY, secure=False)
    try:
        # Ругнется если не будет файла.
        minio.stat_object(settings.BUCKET, file_name)

        # А удаление без наличия файла нормально проходит, можно много раз удалить))
        minio.remove_object(settings.BUCKET, file_name)

    except S3Error as err:
        return {"error": str(err)}

    return {"result": "deleted", "name": file_name, "storage": storage}


def load_file_to_storage(file_path: str, object_name: str, storage: str):
    minio = Minio(storage, access_key=settings.ACCESS_KEY, secret_key=settings.SECRET_KEY, secure=False)
    try:
        bucket = minio.bucket_exists(settings.BUCKET)
        if not bucket:
            minio.make_bucket(settings.BUCKET)
            logging.debug("Create new bucket: [{0}]".format(settings.BUCKET))
        result = minio.fput_object(
            bucket_name=settings.BUCKET,
            object_name=object_name,
            file_path=file_path,
            part_size=PART_SIZE,
            num_parallel_uploads=PARALLEL_UPLOADS,
        )
    except S3Error as err:
        return {"error": str(err)}
    else:
        logging.debug(
            "created {0} object; etag: {1}, version-id: {2}".format(result.object_name, result.etag, result.version_id)
        )
    return {"result": "uploaded", "name": result.object_name, "storage": storage, "etag": result.etag}
