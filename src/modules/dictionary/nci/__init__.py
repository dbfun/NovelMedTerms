from typing import Optional

from src.modules.dictionary import TermDTO, UmlsMetathesaurus
from src.modules.dictionary.umls_dictionary_module import UmlsDictionaryModule
from src.modules.module import ModuleInfo


class Nci(UmlsMetathesaurus):
    """
    Вспомогательный класс для работы с NCI - National Cancer Institute Thesaurus.
    """

    def name(self) -> str:
        return "NCI"

    def dict(self):
        return self._onto["NCI"]

    def search(self, term: str) -> Optional[TermDTO]:
        for concept in self.dict().search(term):
            return TermDTO(ref_id=concept.name)

        return None


class DictionaryNci(UmlsDictionaryModule):
    """
    Модуль поиска термина в словаре NCI.
    """

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="dictionary", type="NCI")

    def dictionary(self) -> UmlsMetathesaurus:
        return Nci()
