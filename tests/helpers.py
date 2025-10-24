"""
Вспомогательные функции для тестирования.
"""
from contextlib import contextmanager
from typing import Any
from unittest.mock import Mock

from src.container import container


@contextmanager
def mock_service(service_name: str, mock_instance: Any = None):
    """
    Context manager для подмены сервиса в контейнере.

    Args:
        service_name: Имя атрибута в контейнере (например, 'pubmed_fetcher')
        mock_instance: Mock объект или None для автоматического создания

    Example:
        with mock_service('pubmed_fetcher') as mock_fetcher:
            mock_fetcher.fetch.return_value = [...]
            # Тест использует замоканный сервис
    """
    if mock_instance is None:
        mock_instance = Mock()

    provider = getattr(container, service_name)

    with provider.override(mock_instance):
        yield mock_instance


def reset_container():
    """
    Сбрасывает все переопределения контейнера.
    Полезно для очистки между тестами если используются
    переопределения на уровне класса или модуля.
    """
    container.reset_last_overriding()
