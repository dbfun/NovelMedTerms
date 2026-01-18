from abc import ABC, abstractmethod

from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.orm.models import Dictionary
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

    def _load_dictionaries(self, session: Session, dict_names: set[str]) -> list[Dictionary]:
        """
        Получение списка словарей из БД для дальнейшей подстановки в SQL.

        Args:
            session: сессия SQLAlchemy
            dict_names: список названий словарей

        Returns:
            Список словарей из БД
        """
        dictionaries: list[Dictionary] = session.query(Dictionary).filter(Dictionary.name.in_(dict_names)).all()

        loaded_dictionaries = set([obj.name for obj in dictionaries])

        if dict_names != loaded_dictionaries:
            raise RuntimeError(
                f"Передан неверный список словарей: {dict_names}, загружены: {loaded_dictionaries}")

        return dictionaries
