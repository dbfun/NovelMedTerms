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

    def test_store_in_db(self, valid_article):
        """Проверка, что изменения сохраняются в БД"""

        with container.db_session() as session:
            session.add(valid_article)
            session.commit()

        # Проверяем, что статья сохранилась в БД
        with container.db_session() as session:
            saved_article = session.query(Article).filter_by(pmid="12345").first()
            assert saved_article is not None
            assert saved_article.title == "Test Title"

    def test_store_in_db_2(self, valid_article):
        """
        Проверка, что новый тест получает чистую БД - проверка на отдельной таблице.
        Прошлый тест добавил в таблицу данные.
        """

        with container.db_session() as session:
            saved_article = session.query(Article).filter_by(pmid="12345").first()
            assert saved_article is None

        self.test_store_in_db(valid_article)
