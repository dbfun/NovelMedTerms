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

Для работы требуется БД Postgres, которую можно развернуть в docker-контейнере:

```bash
docker compose up -d
```

## Тестирование

Для тестирования - сделать аналогичное действие с .env-файлом, но файл находится в каталоге tests:

```bash
cp tests/.env.dist tests/.env
vim tests/.env
```

Запуск тестов:

```bash
pytest
```

## Работа с системой

### Запуск системы

Сценарий использования:

* скопировать файл `workflow.yaml` в каталог `workflows`
* внести изменения в скопированный файл 
* запустить систему

Пример:

```bash
# Копирование workflow.yaml 
cp workflow.yaml workflows/variant-1.yaml

# Внесение изменений
code workflows/variant-1.yaml

# Активация venv
source .venv/bin/activate

# Запуск системы
LOG_LEVEL=info python workflow.py workflows/variant-1.yaml
```

