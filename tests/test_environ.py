import os


class TestEnviron:
    def test_load_test_config(self):
        assert os.environ["APP_ENV"] == "testing"
