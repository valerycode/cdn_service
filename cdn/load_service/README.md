### Сервис загрузки файлов из одного хранилища Minio в другое
API - FastAPI + Celery. В качестве очереди для Celery - Redis. 
Отдельно поднимается контейнер с Flower - Dashboard для Сelery

### Endpoints
* /ping - отвечает "pong"
* POST /v1/tasks/sync - получает задание на синхронизацию:
'{
"delete": [{"movie_id": "string"}],
"upload": [{"movie_id": "string", "storage_url": "string"}]
 }
'

### Запуск
`make run-storage` - запускает два контейнера minio на портах 9010/1 и 9020/1 (логин `root` пароль `123456qwe`)
* minio_1: http://localhost:9011
* minio_2: http://localhost:9021  

`.env.s3ls.example` переименовать в `.env.s3ls` - используется для запуска сервиса в докере  
`make run-service` - запускает 6 контейнеров, составляющие сервис загрузки  
* Dashboard доступен на http://localhost:5555
* API http://localhost:8000/docs

### Тесты
`.env.test.example` переименовать в `.env.test`
`make run-test-env` - запускает тестовое окружение для интеграционного теста  (tests/units/test_copy_delete.py)  
`make test` - запуск тестов