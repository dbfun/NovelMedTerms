from src.modules.module import Module
from src.modules.module_registry import register_module


@register_module(module="fetcher", type="pubmed")
class PubMedFetcher(Module):
    """Модуль для получения статей из PubMed."""

    def __init__(self, term: str):
        self.term = term

    def handle(self):
        pass
