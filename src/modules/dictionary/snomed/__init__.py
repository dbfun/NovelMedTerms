from typing import Optional

from src.modules.dictionary import TermDTO, UmlsMetathesaurus
from src.modules.dictionary.umls_dictionary_module import UmlsDictionaryModule
from src.modules.module import ModuleInfo


class Snomed(UmlsMetathesaurus):
    """
    Вспомогательный класс для работы с SNOMED CT.
    """

    def name(self) -> str:
        return 'SNOMED CT'

    def dict(self):
        return self._onto["SNOMEDCT_US"]

    def search(self, term: str) -> Optional[TermDTO]:
        for concept in self.dict().search(term):
            return TermDTO(ref_id=concept.name)

        return None


class DictionarySnomed(UmlsDictionaryModule):
    """
    Модуль поиска термина в словаре SNOMED CT.
    """

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="dictionary", type="SNOMED CT")

    def dictionary(self) -> UmlsMetathesaurus:
        return Snomed()
