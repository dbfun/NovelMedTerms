from sqlalchemy import text

from src.orm.database import (create_engine_from_config, create_session_factory_from_engine, DatabaseConfig)


class TestOrmDatabase:
    """Тесты для src.orm.database."""

    def test_create_engine_from_config(self):
        """Проверка, что create_engine_from_config возвращает engine."""
        engine = create_engine_from_config(DatabaseConfig())
        assert engine is not None

    def test_create_session_factory_from_engine(self):
        """Проверка, что create_session_factory_from_engine возвращает session."""
        engine = create_engine_from_config(DatabaseConfig())
        session_factory = create_session_factory_from_engine(engine)
        assert session_factory is not None

    def test_get_db_session(self):
        """Проверка, что можно подключиться к БД и выполнить запрос."""
        engine = create_engine_from_config(DatabaseConfig())
        session_factory = create_session_factory_from_engine(engine)
        with session_factory() as session:
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1
