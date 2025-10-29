import pytest

from src.config.database import DatabaseConfig


class TestDatabaseConfig():

    @pytest.fixture
    def db_env(self, monkeypatch):
        monkeypatch.setenv("DB_USER", "user")
        monkeypatch.setenv("DB_PASSWORD", "password")
        monkeypatch.setenv("DB_HOST", "host")
        monkeypatch.setenv("DB_PORT", "port")
        monkeypatch.setenv("DB_NAME", "database")

    def test_db_url(self, db_env):
        """Проверка валидности строки подключения"""
        assert DatabaseConfig().db_url() == "postgresql+psycopg://user:password@host:port/database"
