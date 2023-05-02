from faker import Faker
from fastapi import FastAPI

from src.storages import StorageWorker

app = FastAPI()

fake = Faker()

storage_worker = StorageWorker()


async def get_storage_worker():
    if storage_worker.cdn_storages:
        return storage_worker
    await storage_worker.create_storage_list()
    return storage_worker
