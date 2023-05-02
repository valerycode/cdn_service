Админ панель для работы с кинопроизведениями, жанрами и участниками

Перед началом работы с админкой на проде необходимо выполнить следующие команды(в режиме разработки можно выполнить данные шаги с помощью команды `admin-movies-init`):

1. Применить миграции
```
docker compose exec admin_movies python manage.py migrate
```
2. Создать суперпользователя
```
docker compose exec admin_movies python manage.py createsuperuser
```
3. Загрузить статические файлы
```
docker compose exec admin_movies python manage.py collectstatic --no-input
```