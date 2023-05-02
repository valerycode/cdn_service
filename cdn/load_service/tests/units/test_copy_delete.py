import http
from pathlib import Path
from time import sleep

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from minio import Minio

from core.api_key import get_api_key_header

BASE_DIR = Path(__file__).parent.parent
ENV_TEST = BASE_DIR / ".env.test"
load_dotenv(ENV_TEST, override=True)

from core.config import settings  # noqa E402
from service import app  # noqa E402

S3LS_API_KEY = settings.API_KEY
S3LS_ACCESS_KEY = settings.ACCESS_KEY
S3LS_SECRET_KEY = settings.SECRET_KEY
S3LS_BUCKET_NAME = settings.BUCKET

HOME_S3_HOST = "localhost:9000"
SOURCE_S3_HOST = "localhost:9010"
SOURCE_S3_HOST_DOCKER = "http://minio-src:9000"

FILES_COUNT = 10

filelist = [f"file_{n}" for n in range(FILES_COUNT)]


class ByteGenerator:
    def __init__(self, length):
        self.length = length
        self.total_read = 0

    def read(self, size):
        if self.total_read >= self.length:
            return b""
        read_size = size if self.total_read + size <= self.length else self.length - self.total_read
        self.total_read += read_size
        return b"a" * read_size


def create_s3_files(files: list[str]) -> list[tuple]:
    source_minio = Minio(SOURCE_S3_HOST, access_key=S3LS_ACCESS_KEY, secret_key=S3LS_SECRET_KEY, secure=False)
    if not source_minio.bucket_exists(S3LS_BUCKET_NAME):
        source_minio.make_bucket(S3LS_BUCKET_NAME)
    file_list = []
    size = 15 * 1024 * 1024
    for filename in files:
        data = ByteGenerator(size)  # 15 Mb
        source_minio.put_object(S3LS_BUCKET_NAME, filename, data, length=-1, part_size=10 * 1024 * 1024)
        file_list.append((filename, size))

    return file_list


def list_s3_files(host: str) -> list[tuple]:
    home_minio = Minio(host, access_key=S3LS_ACCESS_KEY, secret_key=S3LS_SECRET_KEY, secure=False)
    objects = home_minio.list_objects(S3LS_BUCKET_NAME)
    return [(obj.object_name, obj.size) for obj in objects]


def clear_home_s3():
    home_minio = Minio(HOME_S3_HOST, access_key=S3LS_ACCESS_KEY, secret_key=S3LS_SECRET_KEY, secure=False)
    objects = home_minio.list_objects(S3LS_BUCKET_NAME)
    for obj in objects:
        home_minio.remove_object(S3LS_BUCKET_NAME, obj.object_name)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client_app:
        yield client_app


@pytest.fixture(scope="session")
def create_files():
    new_files = create_s3_files(filelist)
    clear_home_s3()
    sleep(1)
    return new_files


def test_copy(create_files, client):
    lst_copy = create_files[: FILES_COUNT // 2]
    sync_data = {"upload": [{"movie_id": file[0], "storage_url": SOURCE_S3_HOST_DOCKER} for file in lst_copy]}

    result = client.post("/v1/tasks/sync", json=sync_data, headers=get_api_key_header())
    assert result.status_code == http.HTTPStatus.OK

    sleep(3)
    s3_files = list_s3_files(HOME_S3_HOST)

    assert set(s3_files) == set(lst_copy)


def test_delete_and_copy(create_files, client):
    lst_delete = create_files[: FILES_COUNT // 2]
    lst_copy = create_files[FILES_COUNT // 2 :]  # noqa E203
    sync_data = {
        "delete": [{"movie_id": file[0]} for file in lst_delete],
        "upload": [{"movie_id": file[0], "storage_url": SOURCE_S3_HOST_DOCKER} for file in lst_copy],
    }

    result = client.post("/v1/tasks/sync", json=sync_data, headers=get_api_key_header())
    assert result.status_code == http.HTTPStatus.OK

    sleep(3)
    s3_files = list_s3_files(HOME_S3_HOST)

    assert set(s3_files) == set(lst_copy)


def test_delete(create_files, client):
    lst_delete = create_files[FILES_COUNT // 2 :]  # noqa E203
    sync_data = {"delete": [{"movie_id": file[0]} for file in lst_delete]}
    result = client.post("/v1/tasks/sync", json=sync_data, headers=get_api_key_header())
    assert result.status_code == http.HTTPStatus.OK

    sleep(1)
    s3_files = list_s3_files(HOME_S3_HOST)

    assert len(s3_files) == 0
