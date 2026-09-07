# The lesson uses two-word goals: make build frontend / make run backend.
.DEFAULT_GOAL := all
SERVICES := $(filter frontend backend,$(MAKECMDGOALS))
ifeq ($(strip $(SERVICES)),)
SERVICES := frontend backend
endif
FRONTEND_IMAGE ?= taski-frontend
BACKEND_IMAGE ?= taski-backend
.PHONY: all build run frontend backend network build-frontend build-backend run-frontend run-backend clear logs
all: build
	$(MAKE) run
build: $(addprefix build-,$(SERVICES))
frontend backend:
	@:
build-frontend:
	docker build -t $(FRONTEND_IMAGE) ./frontend
build-backend:
	docker build -t $(BACKEND_IMAGE) ./backend
network:
	docker network inspect taski-network >/dev/null 2>&1 || docker network create taski-network
	docker volume create taski-data
run: $(addprefix run-,$(SERVICES))
run-backend: network
	docker run --rm --network taski-network -v taski-data:/data -e SQLITE_PATH=/data/db.sqlite3 $(BACKEND_IMAGE) python manage.py migrate --noinput
	docker run --name taski-backend -d --network taski-network -v taski-data:/data -e SQLITE_PATH=/data/db.sqlite3 -p 127.0.0.1:8000:8000 $(BACKEND_IMAGE)
# Nginx resolves the backend name at startup.
ifeq ($(words $(SERVICES)),2)
run-frontend: run-backend
endif
run-frontend: network
	docker run --name taski-frontend -d --network taski-network -p 127.0.0.1:3000:80 $(FRONTEND_IMAGE)
clear:
	@for container in taski-frontend taski-backend; do \
		if docker container inspect $$container >/dev/null 2>&1; then \
			docker rm -f $$container || exit $$?; \
		fi; \
	done
logs:
	docker logs taski-backend
	docker logs taski-frontend
