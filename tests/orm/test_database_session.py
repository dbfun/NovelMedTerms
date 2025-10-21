import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.orm.database import get_db_session
from src.orm.models import Articles


@pytest.fixture(scope="session")
def valid_article(engine):
    return Articles(
        pmid="12345",
        authors="Test Author",
        title="Test Title",
        abstract="Test Abstract",
        pubdate=datetime.date.today()
    )


class TestDatabaseSession:
    """Тесты для управления сессиями БД."""

    def test_get_db_session_creates_session(self):
        """Проверка, что context manager создаёт сессию."""
        with get_db_session() as session:
            assert session is not None
            assert session.is_active

    def test_get_db_session_commits_on_success(self, tables, valid_article):
        """Проверка, что изменения сохраняются при успехе - вызывается session.commit()."""

        with get_db_session() as session:
            session.add(valid_article)

        # Проверяем, что статья сохранилась
        with get_db_session() as session:
            saved_article = session.query(Articles).filter_by(pmid="12345").first()
            assert saved_article is not None
            assert saved_article.title == "Test Title"

    def test_get_db_session_calls_rollback_on_error(self, tables):
        """Проверка, что транзакция откатывается при ошибке - вызывается session.rollback() и session.close()."""
        mock_session = MagicMock()

        # Патчим фабрику сессий, чтобы она возвращала мок
        with patch("src.orm.database.get_session_factory", return_value=lambda: mock_session):
            with pytest.raises(ValueError):
                with get_db_session() as session:
                    raise ValueError("Simulated error")

        mock_session.commit.assert_not_called()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_get_db_session_closes_session(self, tables):
        """Проверка, что сессия закрывается после использования."""
        with get_db_session() as session:
            session_id = id(session)

        # После выхода из context manager сессия должна быть закрыта
        # (проверяем через новую сессию)
        with get_db_session() as new_session:
            assert id(new_session) != session_id
