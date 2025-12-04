from typing import Optional

from src.modules.dictionary import TermDTO, UmlsMetathesaurus
from src.modules.dictionary.umls_dictionary_module import UmlsDictionaryModule
from src.modules.module import ModuleInfo


class Who(UmlsMetathesaurus):
    """
    Вспомогательный класс для работы с WHO - WHO Dictionary.
    """

    def name(self) -> str:
        return 'WHO'

    def dict(self):
        return self._onto["WHO"]

    def search(self, term: str) -> Optional[TermDTO]:
        for concept in self.dict().search(term):
            return TermDTO(ref_id=concept.name)

        return None


class DictionaryWho(UmlsDictionaryModule):
    """
    Модуль поиска термина в словаре WHO.
    """

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="dictionary", type="WHO")

    def dictionary(self) -> UmlsMetathesaurus:
        return Who()
