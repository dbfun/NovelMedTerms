from typing import Optional

from src.modules.dictionary import TermDTO, Umls


class Snomed(Umls):
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
