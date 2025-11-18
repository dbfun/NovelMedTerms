from abc import ABC, abstractmethod

from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.orm.models.module import Module as DbModule
from src.workflow import Experiment


class ModuleInfo(BaseModel):
    """Информация о модуле. Служит для идентификации модуля в системе."""
    module: str
    type: str

    def name(self) -> str:
        """Название модуля в виде строки"""
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

    @property
    def experiment(self) -> Experiment:
        return self._experiment

    @experiment.setter
    def experiment(self, val: Experiment) -> None:
        if not val or not isinstance(val, Experiment):
            raise ValueError("Недопустимое значение")
        self._experiment = val

    def _register_module_in_db(self, session: Session) -> int:
        """
        Регистрация модуля в БД.

        Args:
            session: сессия SQLAlchemy

        Returns:
            id модуля
        """
        name = self.info().name()
        module = session.query(DbModule).filter_by(name=name).first()

        if not module:
            module = DbModule(name=name)
            session.add(module)
            session.flush()

        return module.id
