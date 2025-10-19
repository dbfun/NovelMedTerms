"""
Инициализация проекта.
"""
from src.config.database import sync_engine, sessionLocal, Base
from src.orm.models import Articles


def create_tables():
    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)


create_tables()
