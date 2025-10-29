import os


class TestEnviron:

    def test_load_test_config(self):
        """Проверка, что запуск происходит на тестовом окружении"""
        assert os.environ["APP_ENV"] == "testing"
