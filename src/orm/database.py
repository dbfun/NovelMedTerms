from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy import create_engine, Engine

from src.config.database import DatabaseConfig


class BaseModel(DeclarativeBase):
    """Базовый класс для всех ORM моделей."""
    pass


# Глобальные переменные (ленивая инициализация)
_engine: Engine | None = None
_session_factory: sessionmaker | None = None


# get_engine()
# Соединение с БД
# Пул соединений создаётся один раз, можно использовать для всех сессий
#
# get_session_factory()
# Фабрика сессий
# Нужно создавать сессии многократно, без пересоздания engine
#
# get_db_session()
# Конкретная сессия
# Удобно для работы в коде, особенно с with

def get_engine() -> Engine:
    """
    Возвращает singleton instance SQLAlchemy Engine.
    Создаётся только при первом вызове.
    """
    global _engine

    if _engine is None:
        _engine = create_engine(
            url=DatabaseConfig().db_url(),
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Проверка живости соединения
        )

    return _engine


def get_session_factory() -> sessionmaker:
    """Возвращает session factory для создания сессий."""
    global _session_factory

    if _session_factory is None:
        engine = get_engine()
        _session_factory = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
        )

    return _session_factory


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager для безопасной работы с сессией БД.

    Автоматически:
    - Создаёт сессию
    - Делает commit при успехе
    - Делает rollback при ошибке
    - Закрывает сессию

    Example:
        with get_db_session() as session:
            article = Articles(pmid="123", ...)
            session.add(article)
            # commit выполнится автоматически
    """
    session_factory = get_session_factory()
    session = session_factory()

    try:
        yield session
        # Коммит при успешном выполнении
        session.commit()
    except Exception:
        # Откат транзакции при ошибке
        session.rollback()
        raise
    finally:
        # Возвращает соединение в пул
        session.close()
