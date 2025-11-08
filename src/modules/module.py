from abc import ABC, abstractmethod

from pydantic import BaseModel


class ModuleInfo(BaseModel):
    module: str
    type: str

    def name(self) -> str:
        return f"{self.module}-{self.type}"

class Module(ABC):
    """Абстрактный модуль"""

    @staticmethod
    @abstractmethod
    def info() -> ModuleInfo:
        """Информация о модуле"""
        pass

    @abstractmethod
    def handle(self) -> None:
        """Запуск модуля"""
        pass
