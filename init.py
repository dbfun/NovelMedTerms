"""
Инициализация проекта.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import inspect

from src.container import container
from src.orm import models
from src.orm.database import BaseModel

_ = models  # Защита от удаления линтером.

load_dotenv()
assert os.environ["APP_ENV"] == "production"


def drop_tables():
    engine = container.db_engine()
    BaseModel.metadata.drop_all(engine)
    print("✅ Таблицы удалены")


def create_tables():
    engine = container.db_engine()
    BaseModel.metadata.create_all(engine)
    print("✅ Таблицы созданы")


def check_tables():
    engine = container.db_engine()

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    expected = set(BaseModel.metadata.tables.keys())
    missing = expected - set(tables)
    if missing:
        print(f"⚠️ Отсутствуют таблицы: {missing}")
    else:
        print("✅ Все таблицы успешно созданы:")
        for table in tables:
            print(f" - {table}")


if __name__ == "__main__":
    drop_tables()
    create_tables()
    check_tables()
