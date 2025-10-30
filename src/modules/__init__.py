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
from .ner.pos_based_hybrid import PosBasedHybrid
from .pytest.pytest_module import PytestModule
