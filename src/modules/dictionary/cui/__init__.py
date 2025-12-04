from typing import Optional

from src.modules.dictionary import TermDTO, UmlsMetathesaurus
from src.modules.dictionary.umls_dictionary_module import UmlsDictionaryModule
from src.modules.module import ModuleInfo


class Cui(UmlsMetathesaurus):
    """
    Вспомогательный класс для работы с CUI - Concept Unique Identifier.
    """

    def name(self) -> str:
        return 'CUI'

    def dict(self):
        return self._onto["CUI"]

    def search(self, term: str) -> Optional[TermDTO]:
        for concept in self.dict().search(term):
            return TermDTO(ref_id=concept.name)

        return None


class DictionaryCui(UmlsDictionaryModule):
    """
    Модуль поиска термина в словаре CUI.
    """

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="dictionary", type="CUI")

    def dictionary(self) -> UmlsMetathesaurus:
        return Cui()
