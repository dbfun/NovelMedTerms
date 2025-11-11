from typing import Dict, Tuple, Type

from src.modules.module import Module


class ModuleRegistry:
    """Реестр всех зарегистрированных модулей."""

    def __init__(self):
        self._registry: Dict[Tuple[str, str], Type] = {}

    def register(self, module: str, type: str, module_class: Type[Module]) -> None:
        """
        Зарегистрировать модуль.

        Args:
            module: модуль
            type: тип
            module_class: Python-класс модуля
        """
        key = (module, type)
        if key in self._registry:
            raise ValueError(f"Модуль ({module}, {type}) уже зарегистрирован")
        self._registry[key] = module_class

    def get(self, module: str, type: str) -> Type:
        """
        Получить Python-класс модуля.

        Args:
            module: модуль
            type: тип

        Returns:
            Python-класс модуля
        """
        key = (module, type)
        if key not in self._registry:
            raise KeyError(f"Модуль ({module}, {type}) не зарегистрирован")
        return self._registry[key]


# Глобальный реестр
_global_registry = ModuleRegistry()


def register_module(module: Type[Module]):
    _global_registry.register(module.info().module, module.info().type, module)


def get_module_class(module: str, type: str) -> Type:
    """Получить класс модуля из реестра."""
    return _global_registry.get(module, type)
