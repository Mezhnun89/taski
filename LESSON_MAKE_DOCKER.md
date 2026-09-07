# Практика: Make + Docker

Репозиторий — форк yandex-praktikum/taski. Это учебная конфигурация с React и Django dev-серверами; базовые версии соответствуют примеру курса.

## Запуск

Нужны работающий Docker и GNU Make. На Windows удобно выполнять команды в WSL с интеграцией Docker Desktop.

```sh
git clone https://github.com/Mezhnun89/taski.git
cd taski
make all
```

Открыть http://localhost:3000 — интерфейс Taski. Backend API: http://localhost:8000/api/ или http://localhost:8000/api/tasks/. У корневого адреса backend / нет маршрута, поэтому там ожидается Django 404.

- `make build` собирает образы taski-frontend и taski-backend.
- `make run` создаёт сеть и volume, применяет миграции, запускает контейнеры на портах 3000 и 8000.
- `make all` сначала собирает, затем запускает. Обычный `make` делает то же.
- `make logs` показывает журналы.
- `make clear` удаляет только два контейнера Taski; volume с задачами сохраняется.
- Для повторной сборки работающего проекта: `make clear`, затем `make all`.

Порты привязаны к 127.0.0.1 для локальной практики. Между контейнерами работает сеть taski-network; frontend направляет /api/ на taski-backend:8000. SQLite хранится в volume taski-data. Одноразовый контейнер применяет миграции перед запуском backend.

## Проверка

Workflow Make and Docker выполняет настоящий make all на Ubuntu Runner, проверяет HTTP frontend и backend и создание, обновление, чтение и удаление временной задачи через frontend-прокси. После проверки контейнеры удаляются. Для запуска такой же проверки локально: `python3 scripts/check_taski.py`.

## Что запомнить

Makefile описывает цели и порядок команд. Команды рецепта начинаются с TAB. `.PHONY` гарантирует запуск цели даже при наличии одноимённого файла. `all: build` завершает сборку до запуска рецепта all, в том числе при make -j.

Dockerfile описывает образ. RUN выполняется при сборке, CMD — при запуске контейнера. EXPOSE описывает порт, а публикует его docker run -p.

Документация: https://docs.docker.com/reference/dockerfile/ и https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html

В примере курса есть опечатка task-frontend: везде используется единое имя taski-frontend. Дополнительное упражнение со звёздочкой не входит в это решение.
