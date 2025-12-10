from typing import Optional

from src.modules.dictionary import TermDTO, UmlsMetathesaurus
from src.modules.dictionary.umls_dictionary_module import UmlsDictionaryModule
from src.modules.module import ModuleInfo


class Hpo(UmlsMetathesaurus):
    """
    Вспомогательный класс для работы с HPO - Human Phenotype Ontology.
    """

    def name(self) -> str:
        return "HPO"

    def dict(self):
        return self._onto["HPO"]

    def search(self, term: str) -> Optional[TermDTO]:
        for concept in self.dict().search(term):
            return TermDTO(ref_id=concept.name)

        return None


class DictionaryHpo(UmlsDictionaryModule):
    """
    Модуль поиска термина в словаре HPO.
    """

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="dictionary", type="HPO")

    def dictionary(self) -> UmlsMetathesaurus:
        return Hpo()
