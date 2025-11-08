"""
Регистрация модулей.

При каждом "import" запускается декоратор "@register_module", который регистрирует модуль.

Следующий код не будет работать без этого файла:

from src.container import container

module = container.module(
    module="fetcher",
    type="pubmed-central",
    term="filter",
)
"""
from src.modules.module_registry import register_module

from .cleaner.database import CleanerDatabase
from .fetcher.pubmed import PubMedCentralFetcher
from .ner.pos_based_hybrid import PosBasedHybrid
from .pytest.pytest_module import PytestModule

register_module(CleanerDatabase)
register_module(PubMedCentralFetcher)
register_module(PosBasedHybrid)
register_module(PytestModule)
