from typing import Dict, Tuple, Type


class ModuleRegistry:
    """Реестр всех зарегистрированных модулей."""

    def __init__(self):
        self._registry: Dict[Tuple[str, str], Type] = {}

    def register(self, module: str, type: str, module_class: Type) -> None:
        """Зарегистрировать модуль."""
        key = (module, type)
        if key in self._registry:
            raise ValueError(f"Модуль ({module}, {type}) уже зарегистрирован")
        self._registry[key] = module_class

    def get(self, module: str, type: str) -> Type:
        """Получить класс модуля."""
        key = (module, type)
        if key not in self._registry:
            raise KeyError(f"Модуль ({module}, {type}) не зарегистрирован")
        return self._registry[key]


# Глобальный реестр
_global_registry = ModuleRegistry()


def register_module(module: str, type: str):
    """Декоратор для регистрации модуля."""

    def decorator(cls):
        _global_registry.register(module, type, cls)
        return cls

    return decorator


def get_module_class(module: str, type: str) -> Type:
    """Получить класс модуля из реестра."""
    return _global_registry.get(module, type)
