# CDN for online cinema(educational project)

## Technologies:
Python 3, Django, FastAPI, Docker, Docker-Compose, NGINX, PostgreSQL, Redis, Celery, SQLAlchemy

### Launching Services

Rename `env.example` to `.env`, rename `.minio_jwt_example` to `.minio_jwt` in the `/prometheus` folder, then execute `make dev-run`.

### Monitoring

Prometheus is used for monitoring. During development and debugging, you can build graphs at http://localhost:9090 using PromQL. Specifically, you can check the number of files in the bucket with the expression `minio_bucket_usage_object_total{bucket="movies", instance="nginx-minio-0:80"}`, and the free disk space with `minio_cluster_capacity_usable_free_bytes{instance="nginx-minio-0:80"}`.
These data can also be obtained through the Prometheus HTTP API when requesting from the container (Minio updates data once per minute).

```python
import requests

data = {"query": 'minio_bucket_usage_object_total{bucket="movies",instance="minio-0:9000"}'}

response = requests.get("http://prometheus:9090/api/v1/query", params=data)
print(response.json())

response = requests.post("http://prometheus:9090/api/v1/query", data=data)
print(response.json())
```
