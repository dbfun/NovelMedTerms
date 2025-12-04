from typing import Optional

from src.modules.dictionary import TermDTO, UmlsMetathesaurus
from src.modules.dictionary.umls_dictionary_module import UmlsDictionaryModule
from src.modules.module import ModuleInfo


class DrugBank(UmlsMetathesaurus):
    """
    Вспомогательный класс для работы с DrugBank - молекулы, механизмы, биохимия, экспериментальные препараты.
    """

    def name(self) -> str:
        return 'DrugBank'

    def dict(self):
        return self._onto["DRUGBANK"]

    def search(self, term: str) -> Optional[TermDTO]:
        for concept in self.dict().search(term):
            return TermDTO(ref_id=concept.name)

        return None


class DictionaryDrugBank(UmlsDictionaryModule):
    """
    Модуль поиска термина в словаре DrugBank.
    """

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="dictionary", type="DrugBank")

    def dictionary(self) -> UmlsMetathesaurus:
        return DrugBank()
