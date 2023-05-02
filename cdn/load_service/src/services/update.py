import backoff
import httpx

from core.api_key import get_api_key_header
from core.config import settings
from models.update import Updates
from services.storage import storage

"""
Функции для отправки данных на сервер синхронизации
do_update() - проверяет список в редис, если там есть данные - отправляет на сервер
если отправка проходит успешно - удаляет отправленные данные из списка
send_heartbeat() - отправляет ping на сервер
Запускать их планируется из Celery
"""


def post_message_to_server(url: str, message: dict) -> bool:
    """
    Отправляем POST на url с сообщением message (в json)
    Если ответ 200 - возвращаем True
    """
    headers = get_api_key_header()
    try:
        response = httpx.post(url=url, headers=headers, json=message, timeout=1)
        response.raise_for_status()

    except httpx.HTTPError:
        return False

    return True


@backoff.on_predicate(backoff.expo, max_tries=5)
def send_updates(updates: Updates) -> bool:
    """
    Отправляет обновления на сервер синхронизации
    если все ОК - возвращает True
    """
    sync_url = settings.SYNC_URI.format(storage_id=settings.HOME_STORAGE_ID)
    body = updates.dict()
    return post_message_to_server(sync_url, body)


@backoff.on_predicate(backoff.expo, max_tries=3)
def send_heartbeat() -> bool:
    """Отправляет ping сообщение на sync сервер"""
    if not settings.HEARTBEAT_URI:
        return True

    heartbeat_url = settings.HEARTBEAT_URI.format(storage_id=settings.HOME_STORAGE_ID)
    heartbeat_message = {"ping": "pong"}
    return post_message_to_server(heartbeat_url, heartbeat_message)


def no_changes():
    return not storage.count()


def do_update() -> bool:
    """
    Отправляет данные для обновления серверу синхронизации.
    Возвращает True если нет данных или данные отправлены удачно
    """
    # если нет данных для обновления - выходим
    if no_changes():
        return True

    # получаем список обновлений
    updates = storage.get_updates()
    count = len(updates.items)

    # отправляем обновления
    result = send_updates(updates)

    # если все хорошо - стираем из списка
    if result:
        storage.delete(count)

    return result
