from abc import ABC, abstractmethod


class Module(ABC):
    """Абстрактный модуль"""

    @abstractmethod
    def handle(self):
        """Запуск модуля"""
        pass
