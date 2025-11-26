"""
Регистрация модулей.

При создании нового модуля его следует зарегистрировать в этом файле.

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
from .dictionary.mesh import DictionaryMesh
from .dictionary.snomed import DictionarySnomed
from .fetcher.pubmed import PubMedCentralFetcher
from .ner.pos_based_hybrid import PosBasedHybrid
from .output.excel import ExcelOutput
from .output.charts import ChartsOutput
from .pytest.pytest_module import PytestModule

register_module(CleanerDatabase)
register_module(PubMedCentralFetcher)
register_module(PosBasedHybrid)
register_module(PytestModule)
register_module(DictionaryMesh)
register_module(DictionarySnomed)
register_module(ExcelOutput)
register_module(ChartsOutput)
