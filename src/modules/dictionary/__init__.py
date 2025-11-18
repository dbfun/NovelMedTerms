from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from owlready2 import default_world, get_ontology


@dataclass
class TermDTO:
    """
    Data Transfer Object для терминов из словаря
    """
    ref_id: str


class Umls(ABC):
    """
    Вспомогательный класс для работы с UMLS (MeSH и другими словарями) через библиотеку owlready2.

    Документация: https://owlready2.readthedocs.io/en/latest/pymedtermino2.html
    """

    _onto = None

    def __init__(self):
        self._load_dict()

    @classmethod
    def _load_dict(cls):
        """
        Загрузка словаря в библиотеку owlready2. Выполняется только 1 раз.
        """
        if Umls._onto is not None:
            return

        filename = Path("resources/dictionaries/umls/pym.sqlite3")
        if not filename.exists():
            raise FileNotFoundError(f"Файл {filename} должен быть создан скриптом init.py. См. README.md")

        default_world.set_backend(filename=filename)
        Umls._onto = get_ontology("http://PYM/").load()

    @abstractmethod
    def name(self) -> str:
        """Название словаря"""
        pass

    @abstractmethod
    def dict(self):
        """Ссылка на словарь"""
        pass

    @abstractmethod
    def search(self, term: str) -> Optional[TermDTO]:
        """Поиск термина в словаре"""
        pass
