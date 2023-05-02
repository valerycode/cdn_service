import pytest

import services.update
from models.update import Actions, UpdateItem
from services.storage import storage
from services.update import do_update, send_heartbeat

messages = []


def stub_post_message(url: str, message: dict) -> bool:
    messages.append(message)
    return True


@pytest.fixture()
def no_sync(mocker):
    mocker.patch.object(services.update, "post_message_to_server", new=stub_post_message)
    messages.clear()


def test_heartbeat(no_sync):
    """Проверка на отправку сообщений heartbeat"""
    ping_message = {"ping": "pong"}

    assert send_heartbeat() is True
    assert ping_message in messages


def test_update(no_sync):
    """Проверка на отправку сообщений синхронизации"""
    storage.delete(storage.count())

    item_0 = UpdateItem(action=Actions.DELETE, movie_id="file_0")
    item_1 = UpdateItem(action=Actions.DELETE, movie_id="file_1")
    item_2 = UpdateItem(action=Actions.UPLOAD, movie_id="file_2")
    item_3 = UpdateItem(action=Actions.UPLOAD, movie_id="file_3")

    storage.add_update(item_0)
    storage.add_update(item_1)
    storage.add_update(item_2)
    storage.add_update(item_3)

    assert storage.count() == 4

    do_update()

    assert storage.count() == 0
    assert len(messages) == 1

    msg = messages[0]
    assert len(msg["items"]) == 4

    assert item_0.dict() in msg["items"]
    assert item_1.dict() in msg["items"]
    assert item_2.dict() in msg["items"]
    assert item_3.dict() in msg["items"]
