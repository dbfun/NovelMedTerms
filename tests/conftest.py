"""
Механика создания БД и ее очистки позаимствована из этого gist:
https://gist.github.com/kissgyorgy/e2365f25a213de44b9a2?utm_source=chatgpt.com
"""
import os

import pytest
from dotenv import load_dotenv

from src.orm import models
from src.orm.database import get_engine, BaseModel

_ = models  # Защита от удаления линтером.

load_dotenv()

# Защита от запуска на production окружении
assert os.environ["APP_ENV"] == "testing"


@pytest.fixture(scope="session")
def engine():
    return get_engine()


@pytest.fixture(scope="session")
def tables(engine):
    BaseModel.metadata.create_all(engine)
    try:
        yield
    finally:
        BaseModel.metadata.drop_all(engine)
