
### Запуск

docker compose up -d --build sync-service minio-0 createbuckets


### Тесты

Тестирование на хосте

Переименовать в ./cdn/sync_service .env.test.example в .env.test
- `make run-test-db` запустить контейнер с тестовой базой данных
- `make test-sync`
- `make stop-test-db` удалить контейнер с тестовой базой данных

### Миграции

Для создания миграций алембику необходимо соединение c базой данных,
поэтому нужно экспортировать переменную окружения перед запуском
команд алембика либо создать локальный .env.local файл и загружать
переменную из него (пример файла в папке).

Команды запускать из папки cdn/sync_service
 - Создать миграцию `alembic revision --autogenerate -m "migration name"`
 - Применить все миграции `alembic upgrade head`
`

