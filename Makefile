# Все команды выполняются из корня проекта. Отступы рецептов — TAB.
.DEFAULT_GOAL := all
.PHONY: all build run clear logs

all: build
	$(MAKE) run

build:
	docker build -t taski-frontend ./frontend
	docker build -t taski-backend ./backend

run:
	docker network inspect taski-network >/dev/null 2>&1 || docker network create taski-network
	docker volume create taski-data
	docker run --rm --network taski-network -v taski-data:/data -e SQLITE_PATH=/data/db.sqlite3 taski-backend python manage.py migrate --noinput
	docker run --name taski-backend -d --network taski-network -v taski-data:/data -e SQLITE_PATH=/data/db.sqlite3 -p 127.0.0.1:8000:8000 taski-backend
	docker run --name taski-frontend -d --network taski-network -p 127.0.0.1:3000:3000 taski-frontend

# Удаляются только два контейнера проекта. Данные SQLite сохраняются в volume.
clear:
	@for container in taski-frontend taski-backend; do \
		if docker container inspect $$container >/dev/null 2>&1; then \
			docker rm -f $$container || exit $$?; \
		fi; \
	done

logs:
	docker logs taski-backend
	docker logs taski-frontend
