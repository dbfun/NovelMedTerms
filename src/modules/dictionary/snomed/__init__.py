from typing import Optional

import owlready2

from src.modules.dictionary import TermDTO, Umls


class Snomed(Umls):
    """
    Вспомогательный класс для работы с SNOMED CT.
    """

    def name(self) -> str:
        return 'SNOMED CT'

    def dict(self) -> owlready2.pymedtermino2.model.MetaConcept:
        return self.onto["SNOMEDCT_US"]

    def search(self, term: str) -> Optional[TermDTO]:
        for concept in self.dict().search(term):
            return TermDTO(ref_id=concept.name)

        return None
