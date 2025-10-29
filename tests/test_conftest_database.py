import datetime

import pytest

from src.container import container
from src.orm.models import Article


@pytest.fixture(scope="function")
def valid_article() -> Article:
    return Article(
        pmid="12345",
        authors="Test Author",
        title="Test Title",
        abstract="Test Abstract",
        pubdate=datetime.date.today()
    )


class TestConftestDatabase:
    """
    Тесты для проверки подмены рабочей БД на тестовую с откатом изменений.
    @see conftest.py.
    """

    def test_fixture_db_session(self, valid_article, db_session):
        """Проверка фикстуры "db_session" из conftest.py. Данные должны быть сохранены в БД"""
        db_session.add(valid_article)
        db_session.commit()
        saved_article = db_session.query(Article).filter_by(pmid="12345").first()
        assert isinstance(saved_article, Article)

    def test_fixture_override_container_db_session(self, valid_article):
        """Проверка фикстуры "override_container_db_session". Данные должны быть сохранены в БД"""

        with container.db_session() as db_session:
            db_session.add(valid_article)
            db_session.commit()

        # Проверяем, что статья сохранилась в БД
        with container.db_session() as db_session:
            saved_article = db_session.query(Article).filter_by(pmid="12345").first()
            assert isinstance(saved_article, Article)

    def test_fixture_override_container_db_session_2(self):
        """
        Проверка, что новый тест получает чистую БД - проверка на отдельной таблице.
        Прошлый тест добавил в таблицу данные.
        """

        with container.db_session() as session:
            saved_article = session.query(Article).filter_by(pmid="12345").first()
            assert saved_article is None, "База данных не чистая"
