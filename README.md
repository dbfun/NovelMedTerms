# Мультимодальная система обнаружения новой медицинской терминологии

## Установка и настройка проекта

Используется Python 3.12.3.

Установить `.venv`:

* `python3 -m venv .venv`
* `source .venv/bin/activate`
* `pip install -r requirements.txt`

Конфигурация - через .env-файлы.

Скопировать и поменять `.env` файл в корне проекта. Он служит как рабочий конфиг.

```bash
cp .env.dist .env
vim .env
```

Для тестирования - сделать аналогичное действие, но файл находится в каталоге tests:

```bash
cp tests/.env.dist tests/.env
vim tests/.env
```

Для работы требуется БД postgres, которую можно развернуть в docker-контейнере:

```bash
docker compose up -d
```
