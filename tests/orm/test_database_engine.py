from sqlalchemy import text, inspect

from src.orm.database import get_engine


class TestDatabaseEngine:
    """Тесты для engine."""

    def test_get_engine_returns_engine(self):
        """Проверка, что get_engine возвращает engine."""
        engine = get_engine()
        assert engine is not None

    def test_get_engine_returns_same_instance(self):
        """Проверка, что engine - singleton."""
        engine1 = get_engine()
        engine2 = get_engine()
        assert engine1 is engine2

    def test_engine_can_connect(self):
        """Проверка, что можно подключиться к БД."""
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
