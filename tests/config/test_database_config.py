from src.config.database import DatabaseConfig


class TestDatabaseConfig():
    def test_db_url(self):
        """Проверка валидности строки подключения"""
        assert "://" in DatabaseConfig().db_url()
