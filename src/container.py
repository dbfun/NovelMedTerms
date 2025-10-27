"""
Service Container на основе dependency-injector.
Аналог Laravel Service Container для Python.
"""
from contextlib import contextmanager
from typing import Generator

from dependency_injector import containers, providers
from sqlalchemy.orm import sessionmaker, Session

from src.config.database import DatabaseConfig
from src.orm.database import (
    create_engine_from_config,
    create_session_factory_from_engine,
)


@contextmanager
def _get_db_session(session_factory: sessionmaker) -> Generator[Session, None, None]:
    """
    Context manager для безопасной работы с сессией БД.

    Автоматически:
    - Создаёт сессию
    - НЕ делает commit при успехе - чтобы не расходилось с тестами, в которых автоматический коммит не предусмотрен.
    - Делает rollback при ошибке
    - Закрывает сессию

    Example:
        with get_db_session() as session:
            article = Articles(pmid="123", ...)
            session.add(article)
            # commit выполнится автоматически
    """
    session = session_factory()
    try:
        yield session
    except Exception:
        # Откат транзакции при ошибке
        session.rollback()
        raise
    finally:
        # Возвращает соединение в пул
        session.close()


class Container(containers.DeclarativeContainer):
    """
    Главный контейнер зависимостей приложения.

    Регистрирует все сервисы и их зависимости.
    """

    db_engine = providers.Singleton(
        create_engine_from_config,
        config=providers.Singleton(DatabaseConfig),
    )

    db_session_factory = providers.Singleton(
        create_session_factory_from_engine,
        engine=db_engine,
    )

    # В тестах идет замена на сессию с откатом изменений.
    # @see conftest.override_container_db_session
    db_session = providers.Factory(
        _get_db_session,
        session_factory=db_session_factory,
    )


# Глобальный экземпляр контейнера
container = Container()
