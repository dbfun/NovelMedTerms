from contextlib import contextmanager
from typing import Type

from dependency_injector import providers

from src.container import container


@contextmanager
def mock_module(module_name: str, type_name: str, mock_class: Type):
    """
    Временная подмена модуля в контейнере dependency_injector с поддержкой вложенных вызовов.

    Пример:
        with mock_module("fetcher", "pubmed", MockPubMedFetcher):
            module = container.module(module="fetcher", type="pubmed", term="test")
            assert isinstance(module, MockPubMedFetcher)

    После выхода из контекста оригинальный провайдер восстанавливается.
    """

    # Берём "активный" провайдер — без последнего override
    original_provider = container.module.overridden[-1] if container.module.overridden else container.module

    # Создаём провайдер, который решает, что вернуть
    new_provider = providers.Factory(
        lambda module, type, **kwargs: (
            mock_class(**kwargs)
            if module == module_name and type == type_name
            else original_provider(module=module, type=type, **kwargs)
        )
    )

    container.module.override(new_provider)

    try:
        yield
    finally:
        # Снимаем только последний override (Dependency Injector сам управляет стеком)
        container.module.reset_last_overriding()
