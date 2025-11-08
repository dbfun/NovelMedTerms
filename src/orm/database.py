from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from src.config.database import DatabaseConfig


class BaseModel(DeclarativeBase):
    """Базовый класс для всех ORM моделей."""
    pass


# create_engine_from_config()
# Соединение с БД
#
# create_session_factory_from_engine()
# Фабрика сессий
# Нужно создавать сессии многократно, без пересоздания engine
#
# container.db_session()
# Конкретная сессия
# Удобно для работы в коде, особенно с with

def create_engine_from_config(config: DatabaseConfig) -> Engine:
    """Создает engine из конфига."""
    return create_engine(
        url=config.db_url(),
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Проверка живости соединения
    )


def create_session_factory_from_engine(engine: Engine) -> sessionmaker:
    """Создает session factory из engine."""
    return sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )
