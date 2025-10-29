from src.modules.module import Module
from src.modules.module_registry import register_module


@register_module(module="pytest", type="pytest")
class PytestModule(Module):
    """Тестовый модуль для TDD."""

    def __init__(self, param1: str):
        self.param1 = param1

    def handle(self) -> None:
        pass
