"""
Импорт всех модулей в реестр.

Следующий код не будет работать без этого файла:

from src.container import container

module = container.module(
    module="fetcher",
    type="pubmed-central",
    term="filter",
)
"""
from .fetcher.pubmed.pub_med_central_fetcher import PubMedCentralFetcher
from .pytest.pytest_module import PytestModule
