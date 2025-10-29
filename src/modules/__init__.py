"""
Импорт всех модулей в реестр.

Следующий код не будет работать без этого файла:

from src.container import container

type = "pubmed"
term = "filter"

module = container.module(
    module="fetcher",
    type=type,
    term=term,
)
"""
from .fetcher.pubmed.pub_med_fetcher import PubMedFetcher
from .pytest.pytest_module import PytestModule
