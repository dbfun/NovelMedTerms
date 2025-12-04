"""
Вспомогательная утилита для поиска термина в MeSH
"""
from dotenv import load_dotenv

from src.modules.dictionary import UmlsMetathesaurus


class SearchInDict:
    # Список доступных словарей
    available_dictionaries: dict[str, dict[str, str]] = {
        'MeSH': {'module_dir': 'mesh', 'class_name': 'MeSH'},
        'SNOMED': {'module_dir': 'snomed', 'class_name': 'Snomed'},
        'ICD': {'module_dir': 'icd10', 'class_name': 'Icd10'},
        'CUI': {'module_dir': 'cui', 'class_name': 'Cui'},
        'DrugBank': {'module_dir': 'drugbank', 'class_name': 'DrugBank'},
        'GO': {'module_dir': 'go', 'class_name': 'Go'},
        'HPO': {'module_dir': 'hpo', 'class_name': 'Hpo'},
        'NCI': {'module_dir': 'nci', 'class_name': 'Nci'},
        'WHO': {'module_dir': 'who', 'class_name': 'Who'},
    }

    def run(self):
        try:
            dictionaries = self._choice_dictionaries()
            self._search_dialog(dictionaries)
        except KeyboardInterrupt:
            pass

    def _search_dialog(self, dictionaries: list[UmlsMetathesaurus]):
        print("Введите термин для поиска, например Heart Attack, Asthma")
        while True:
            text = input("Термин: ")
            if not text:
                continue

            dictionary: UmlsMetathesaurus
            for dictionary in dictionaries:
                for concept in dictionary.dict().search(text):
                    self._print_concept(concept, dictionary.name())

    def _print_concept(self, concept, dict_name: str) -> None:
        print(f"{dict_name}\t{str(concept.label[0])} [{concept.name}]")

    def _choice_dictionaries(self) -> list[UmlsMetathesaurus]:
        """
        Выбор словарей для поиска.

        Returns:
            Список объектов словарей
        """

        print(f"Введите список словарей для поиска через пробел. Варианты: {" ".join(self.available_dictionaries)}")

        while True:
            text = input("Словари: ")
            if not text:
                continue

            dict_to_load = text.split()

            # Проверка на пустое значение
            if len(dict_to_load) == 0:
                continue

            # Проверка на допустимое значение
            invalid = False
            for dictionary in dict_to_load:
                if dictionary not in self.available_dictionaries:
                    print(f"Неверное значение: {dictionary}")
                    invalid = True
                    break
            if invalid:
                continue

            # Загрузка словарей
            return self._load_dictionaries(dict_to_load)

    def _load_dictionaries(self, dict_to_load: list[str]) -> list[UmlsMetathesaurus]:
        """
        Загрузка словарей из Python-модулей.

        Args:
            dict_to_load: список словарей для загрузки

        Returns:
            Список объектов словарей
        """
        dictionaries = []
        for dictionary in dict_to_load:
            # Динамическое подключение словарей из Python-модулей.
            dict_params = self.available_dictionaries[dictionary]
            module_dir = dict_params.get('module_dir')
            class_name = dict_params.get('class_name')
            module = __import__(f"src.modules.dictionary.{module_dir}", fromlist=[class_name])
            cls = getattr(module, class_name)
            dictionaries.append(cls())

        return dictionaries


if __name__ == "__main__":
    load_dotenv()
    app = SearchInDict()
    app.run()
