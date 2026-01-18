import datetime
import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.orm import Session

from src.container import container
from src.orm import models
from src.orm.database import BaseModel
from src.orm.models import Article
from src.workflow import Experiment

_ = models  # Защита от удаления линтером.

load_dotenv()

# Защита от запуска на production окружении
assert os.environ["APP_ENV"] == "testing"


@pytest.fixture(scope="session")
def db_engine():
    """Создаёт engine для тестовой БД."""
    return container.db_engine()


@pytest.fixture(scope="session")
def db_tables(db_engine):
    """
    Создает все таблицы перед тестами.
    Удаляет все таблицы после завершения всех тестов.

    Механика создания БД и ее очистки позаимствована из этого gist:
    https://gist.github.com/kissgyorgy/e2365f25a213de44b9a2
    """
    BaseModel.metadata.create_all(db_engine)
    try:
        yield
    finally:
        BaseModel.metadata.drop_all(db_engine)


@pytest.fixture(scope="function")
def db_session(db_engine, db_tables):
    """
    Создает транзакционную сессию для каждого теста.

    Механизм:
        1. Открывает connection и транзакцию
        2. Создаёт session, привязанную к этой транзакции
        3. После теста делает rollback
        4. Каждый тест получает чистую БД

    Использование:
        * В тестах: использовать фикстуру `db_session`
        * В рабочем коде: использовать `with container.db_session() as session`

    Основано на:
    https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    """
    connection = db_engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    # Отключаем автоматический commit/rollback для контроля транзакций
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        """
        Автоматически создаёт новый savepoint после каждого commit/rollback.
        Без этого возникнет ошибка, если в коде дважды выполнить db_session.commit()
        """
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function", autouse=True)
def override_container_db_session(db_session):
    """
    Автоматически переопределяет db_session в контейнере для всех тестов.

    Теперь при вызове container.db_session() будет возвращаться
    транзакционная тестовая сессия вместо production версии.
    """
    with container.db_session.override(db_session):
        yield


@pytest.fixture(scope="function")
def valid_article() -> Article:
    """Валидная модель статьи"""
    return Article(
        pmcid="PMC12345",
        authors="Test Author",
        title="Test Title",
        abstract="Test Abstract",
        pubdate=datetime.date.today()
    )


@pytest.fixture(scope="function", autouse=True)
def fake_experiment(tmp_path):
    """Фикстура для Experiment"""
    return Experiment(
        name="Pytest fake experiment",
        description="Fake description",
        directory=str(tmp_path),
        author="Fake author"
    )
