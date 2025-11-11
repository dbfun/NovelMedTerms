"""
Точка входа для запуска workflow.
Подробная информация находится в README.md
"""
import argparse
import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.container import container
from src.workflow import Config

logger = logging.getLogger("workflow")


class Workflow:
    """Класс для запуска workflow из файла workflow.yml"""

    def __init__(self):
        self._setup_log_level()
        self._load_workflow_from_file()

    def _setup_log_level(self):
        """Настройка уровня и формата журналирования"""
        log_level = os.getenv("LOG_LEVEL", "WARNING").upper()
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format="%(levelname)s\t%(name)s: %(message)s"
        )

    def _load_workflow_from_file(self):
        """Чтение управляющей последовательности из файла workflow.yml"""
        parser = argparse.ArgumentParser()
        parser.add_argument("file", type=Path, help="Путь к файлу")
        self.args = parser.parse_args()

        with open(self.args.file, "r", encoding="utf-8") as f:
            self.cfg = Config(**yaml.safe_load(f))

    def run(self):
        """Запуск последовательности стадий"""
        logger.info(self.cfg.experiment.description)

        for stage in self.cfg.stages:
            logger.info(stage.name)
            for module in stage.modules:
                params = module.params or {}
                module_obj = container.module(
                    module=module.module,
                    type=module.type,
                    **params
                )
                module_obj.handle()


if __name__ == "__main__":
    load_dotenv()
    app = Workflow()
    app.run()
