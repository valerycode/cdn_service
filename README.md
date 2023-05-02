### Запуск сервисов

Переименуйте env.example в .env, в папке /prometheus переименуйте .minio_jwt_example
 .minio_jwt. Затем выполните `make dev-run`


### Мониторинг

Для мониторинга используется Prometheus. Графики в процессе разработки и
дебаггинга можно построить на http://localhost:9090 c использованием PromQL.
В частности, количество файлов в бакете можно посмотреть с помощью выражения
`minio_bucket_usage_object_total{bucket="movies", instance="nginx-minio-0:80"}`,
свободное место на диске `minio_cluster_capacity_usable_free_bytes{instance="nginx-minio-0:80"}`
Эти данные также можно получить с помощью  HTTP API Prometheus при запросе из
контейнера (minio обновляет данные раз в минуту)
```
import requests

data = {"query": 'minio_bucket_usage_object_total{bucket="movies",instance="minio-0:9000"}'}

response = requests.get("http://prometheus:9090/api/v1/query", params=data)
print(resposne.json())

response = requests.post("http://prometheus:9090/api/v1/query", data=data)
print(response.json())
```
