from typing import Optional

from src.modules.dictionary import TermDTO, UmlsMetathesaurus
from src.modules.dictionary.umls_dictionary_module import UmlsDictionaryModule
from src.modules.module import ModuleInfo


class MeSH(UmlsMetathesaurus):
    """
    Вспомогательный класс для работы с MeSH.
    """

    def name(self) -> str:
        return "MeSH"

    def dict(self):
        return self._onto["MSH"]

    def search(self, term: str) -> Optional[TermDTO]:
        for concept in self.dict().search(term):
            # Проверка на точное совпадение - не нужна, так как
            # "Heart Attack" возвращает "Myocardial Infarction",
            # что значит, что термин известен системе. Возвращаем первое совпадение.
            # Старый вариант: if concept.label[0].lower() == term.lower(): return TermDTO(ref_id=concept.name)
            return TermDTO(ref_id=concept.name)

        return None


class DictionaryMesh(UmlsDictionaryModule):
    """
    Модуль поиска термина в словаре MeSH.

    Информация о MeSH
    -----------------


    MeSH (Medical Subject Headings) is the NLM controlled vocabulary thesaurus used for indexing articles for PubMed.

    Поиск: https://www.ncbi.nlm.nih.gov/mesh?cmd=search
    """

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="dictionary", type="MeSH")

    def dictionary(self) -> UmlsMetathesaurus:
        return MeSH()
