import logging
from pathlib import Path

from sqlalchemy.orm import Session

from src.modules.module import Module
from src.orm.models import Dictionary


class Output(Module):
    def __init__(self):
        self.logger = logging.getLogger(self.info().name())

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

    def _create_experiment_dir(self):
        """
        Создаем каталог с результатами эксперимента, если его нет
        """
        directory = Path(self.experiment.directory)
        directory.mkdir(parents=True, exist_ok=True)

    def _generate_output_file_path(self, name: str) -> Path:
        """
        Генерация пути к файлу с результатами работы.

        Args:
            name: название файла

        Returns:
            полный путь к файлу
        """
        return Path(self.experiment.directory) / name

    def _print_results(self, handler: type, output_files: list[Path]) -> None:
        output_files = ", ".join([str(file) for file in output_files])
        self.logger.info(f"[{handler.__name__}] результаты сохранены в файлы: {output_files}")
