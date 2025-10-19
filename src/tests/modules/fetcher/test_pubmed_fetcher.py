import pytest
from sqlalchemy import text
from unittest.mock import patch

from src.config.database import sessionLocal, Base, sync_engine
from src.orm.models import Articles


# --- фикстура для тестовой БД ---
@pytest.fixture(scope="function")
def db_session():
    # Создаём таблицы для теста
    Base.metadata.create_all(sync_engine)
    session = sessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(sync_engine)


# --- мок для PubMed ---
MOCK_PUBMED_RESPONSE = [
    {
        "pmid": "123456",
        "title": "Test Article Title",
        "abstract": "Sample abstract",
        "author": "John Doe",
        "pubdate": "2020-01-01",
    },
    {
        "pmid": "789012",
        "title": "Another Article",
        "abstract": "Another sample abstract",
        "author": "Jane Smith",
        "pubdate": "2021-05-03",
    },
]


# --- сам тест ---
def test_import_pubmed_saves_articles_to_db(db_session):
    # Мы ожидаем, что import_pubmed(term, session) добавит статьи в БД.
    with patch("src.modules.fetcher.pubmed.fetch.fetch_from_pubmed", return_value=MOCK_PUBMED_RESPONSE):
        from src.modules.fetcher.pubmed.fetch import import_pubmed

        count = import_pubmed("test term", db_session)

        # Проверяем, что возвращено правильное количество
        assert count == 2

        # Проверяем, что статьи реально были сохранены в БД
        results = db_session.query(Articles).all()
        assert len(results) == 2
        assert results[0].pmid == "123456"
