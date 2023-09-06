.DEFAULT_GOAL := oneshot
COMPOSE_FILE ?= local.yml
SHELL_PREFIX=docker compose exec -e DJANGO_SETTINGS_MODULE=config.settings.local django /entrypoint
RUN_PREFIX=docker compose -f ${COMPOSE_FILE} run --rm -e DJANGO_SETTINGS_MODULE=config.settings.local django

shell:
	${SHELL_PREFIX} /bin/bash

makemigrations:
	${RUN_PREFIX} ./manage.py makemigrations

migrate:
	${SHELL_PREFIX} ./manage.py migrate

oneshot:
	docker compose -f ${COMPOSE_FILE} up -d

restart: stop oneshot

restart.django:
	docker compose -f ${COMPOSE_FILE} restart django

stop:
	docker compose -f ${COMPOSE_FILE} down

destroy:
	docker compose -f ${COMPOSE_FILE} down -v

test:
	${RUN_PREFIX} python -m pytest .

build.cache:
	docker compose -f ${COMPOSE_FILE} build

build.no-cache:
	docker compose -f ${COMPOSE_FILE} build --no-cache

build: build.no-cache

logs:
	docker compose -f ${COMPOSE_FILE} logs -f

logs.%:
	docker compose -f ${COMPOSE_FILE} logs -f $*

createsuperuser:
	docker compose -f ${COMPOSE_FILE} run --rm django python manage.py createsuperuser
