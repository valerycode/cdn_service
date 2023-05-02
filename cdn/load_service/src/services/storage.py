import backoff
from pydantic.error_wrappers import ValidationError
from redis import Redis
from redis.exceptions import RedisError

from core.config import settings
from models.update import UpdateItem, Updates

""" Обертка над редис для хранения списка синхронизации"""

__all__ = ("storage",)


class Storage:
    redis: Redis
    update_key: str = "sync"

    def __init__(self, redis: Redis):
        self.redis = redis

    def add_message(self, message: str):
        self.redis.rpush(self.update_key, message)

    def add_update(self, update: UpdateItem):
        self.add_message(update.json())

    def delete(self, count: int = 0):
        """Удаляет из списка count первых сообщений"""
        self.redis.ltrim(self.update_key, count, -1)

    def get_messages(self):
        return self.redis.lrange(self.update_key, 0, -1)

    def get_updates(self):
        messages = self.get_messages()
        items = []
        for message in messages:
            try:
                update_item = UpdateItem.parse_raw(message)
                items.append(update_item)

            except ValidationError:
                continue

        return Updates(items=items)

    def count(self) -> int:
        return self.redis.llen(self.update_key)

    @backoff.on_predicate(backoff.expo, max_tries=None, max_value=30)
    def check_broker(self) -> bool:
        try:
            self.redis.ping()
        except RedisError:
            return False

        return True


redis = Redis.from_url(settings.STORAGE_BROKER_URI, decode_responses=True)
storage = Storage(redis)
