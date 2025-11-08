from src.modules.module import Module, ModuleInfo


class PytestModule(Module):
    """Тестовый модуль для TDD."""

    def __init__(self, param1: str):
        self.param1 = param1

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="pytest", type="pytest")

    def handle(self) -> None:
        pass
