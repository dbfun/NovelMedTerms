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
from .dictionary.cui import DictionaryCui
from .dictionary.drugbank import DictionaryDrugBank
from .dictionary.go import DictionaryGo
from .dictionary.hpo import DictionaryHpo
from .dictionary.icd10 import DictionaryIcd10
from .dictionary.mesh import DictionaryMesh
from .dictionary.nci import DictionaryNci
from .dictionary.snomed import DictionarySnomed
from .dictionary.who import DictionaryWho
from .fetcher.pubmed import PubMedFetcher
from .fetcher.pubmed_central import PubMedCentralFetcher
from .ner.pos_based_hybrid import PosBasedHybrid
from .output.charts import ChartsOutput
from .output.excel import ExcelOutput
from .pytest.pytest_module import PytestModule

register_module(CleanerDatabase)
register_module(PubMedCentralFetcher)
register_module(PubMedFetcher)
register_module(PosBasedHybrid)
register_module(PytestModule)
register_module(DictionaryMesh)
register_module(DictionarySnomed)
register_module(DictionaryCui)
register_module(DictionaryDrugBank)
register_module(DictionaryGo)
register_module(DictionaryHpo)
register_module(DictionaryIcd10)
register_module(DictionaryNci)
register_module(DictionaryWho)
register_module(ExcelOutput)
register_module(ChartsOutput)
