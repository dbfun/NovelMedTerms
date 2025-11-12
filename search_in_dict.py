"""
Вспомогательная утилита для поиска термина в MeSH
"""
import owlready2
from dotenv import load_dotenv

from src.modules.dictionary.mesh import MeSH
from src.modules.dictionary.snomed import Snomed


class SearchInDict:
    def _print_concept(self, concept: owlready2.pymedtermino2.model.MetaConcept, dict_name: str) -> None:
        print(f"{dict_name}\t{str(concept.label[0])} [{concept.name}]")

    def run(self):
        mesh = MeSH()
        snomed = Snomed()
        print("Введите термин для поиска, например Heart Attack")
        try:
            while True:
                text = input("Термин: ")
                if not text:
                    continue

                for concept in mesh.dict().search(text):
                    self._print_concept(concept, "MeSH")

                for concept in snomed.dict().search(text):
                    self._print_concept(concept, "Snomed")

        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    load_dotenv()
    app = SearchInDict()
    app.run()
