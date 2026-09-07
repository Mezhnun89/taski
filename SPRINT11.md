# Автоматизация сборки приложений — спринт 11

Проект: Taski, исходник https://github.com/yandex-praktikum/taski.
Итоговая практика разрешает GitHub Actions вместо GitLab CI/CD.

## Запуск

Нужны Docker, Make; для проверки — Python 3.

```sh
make all
python3 scripts/check_taski.py
make clear
```

Сайт: http://127.0.0.1:3000; API: http://127.0.0.1:8000/api/tasks/.
Поддерживаются `make build frontend`, `make build backend`, `make build`,
`make run backend`, `make run frontend`, `make run`, `make all`.
При раздельном запуске сначала запускайте backend: Nginx использует его DNS-имя.
`make clear` удаляет только контейнеры Taski, SQLite остаётся в volume `taski-data`.
Это учебный проект с Django runserver и старыми зависимостями исходного задания.

## Сборка и проверка

- Frontend: Node 22 собирает React, Nginx раздаёт build и проксирует `/api/`.
- Backend: отдельный этап устанавливает Python-зависимости; runtime получает их и код.
- Файлы зависимостей копируются раньше исходников, `npm ci` использует lockfile.
- GitHub Actions запускает настоящий `make all` и HTTP CRUD через Nginx.
- `scripts/benchmark_build.py` сравнивает четыре сборки backend: плохой/хороший
  порядок COPY, первая сборка/после изменения manage.py. Результаты и логи —
  артефакт `build-measurements`, а не примерные цифры из урока.
- Отдельная CI-задача сохраняет pip cache по хешу requirements.txt.
  Два запуска позволяют сравнить восстановление кэша и время install + check.
- Размер backend сравнивается с одноэтапным Dockerfile урока. Удаление pip cache
  тоже влияет на размер; multi-stage сам по себе не гарантирует уменьшение.

## Другие CI-платформы

`.gitlab-ci.yml` собирает оба сервиса и публикует теги commit SHA в GitLab Registry.
Требуется runner с privileged Docker-in-Docker и общим TLS volume `/certs/client`.
Registry cache переносит слои между разными runners.

`Jenkinsfile` предназначен для выделенного агента с Docker, Make и Python 3,
Pipeline и Credentials Binding plugins. В Jenkins нужен credential
`dockerhub-credentials` типа Username with password (Docker Hub access token).
Docker daemon агента сохраняет локальный кэш между сборками.
Наличие конфигураций не является подтверждением успешного запуска этих платформ:
фактические результаты фиксируются отдельно после выполнения.

Документация:
- https://docs.docker.com/build/building/multi-stage/
- https://docs.docker.com/build/cache/
- https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching
