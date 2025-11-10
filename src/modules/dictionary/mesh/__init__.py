import logging

from src.modules.module import Module, ModuleInfo


class DictionaryMesh(Module):
    """
    Модуль фильтрации терминов по словарю MeSH.

    Информация о MeSH
    -----------------


    MeSH (Medical Subject Headings) is the NLM controlled vocabulary thesaurus used for indexing articles for PubMed.

    Поиск: https://www.ncbi.nlm.nih.gov/mesh?cmd=search
    """

    def __init__(self):
        self.logger = logging.getLogger(DictionaryMesh.info().name())

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="dictionary", type="mesh")

    def handle(self) -> None:
        pass
