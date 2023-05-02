include .env

auth-init:
	docker compose exec auth flask db upgrade
	docker compose exec auth flask insert-roles
	docker compose exec auth flask createsuperuser --email ${AUTH_SUPERUSER_LOGIN} --password ${AUTH_SUPERUSER_PASSWORD}

admin-movies-init:
	docker compose exec admin_movies python manage.py migrate
	docker compose exec admin_movies python manage.py createsuperuser --noinput --username ${DJANGO_SUPERUSER_USERNAME} --email ${DJANGO_SUPERUSER_EMAIL}
	docker compose exec admin_movies python manage.py collectstatic --no-input

sync-init:
	docker compose exec sync-service alembic upgrade head

dev-run:
	docker compose up --build -d
	sleep 5  # ждем запуск постгрес для применения миграций
	$(MAKE) auth-init
	$(MAKE) admin-movies-init
	$(MAKE) sync-init
	docker compose exec auth python fake_data.py

format:
	black .
	isort .

lint:
	black --check .
	isort --check-only .
	flake8 .


run-test-db:
	docker run --env POSTGRES_USER=user --env POSTGRES_PASSWORD=password --env POSTGRES_DB=test_database \
    	--name test_postgres -p 45432:5432 -d postgres:15.1-alpine

test-sync:
	pytest -s ./cdn/sync_service/app/tests

stop-test-db:
	docker rm --force test_postgres
