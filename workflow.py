"""
Точка входа для запуска workflow.
"""
import argparse
import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.container import container
from src.workflow import Config


class Workflow:
    def __init__(self):
        self.setup_log_level()
        self.load_workflow_from_file()

    def setup_log_level(self):
        log_level = os.getenv("LOG_LEVEL", "WARNING").upper()
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format="%(levelname)s: %(message)s"
        )

    def load_workflow_from_file(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("file", type=Path, help="Путь к файлу")
        self.args = parser.parse_args()

        with open(self.args.file, "r", encoding="utf-8") as f:
            self.cfg = Config(**yaml.safe_load(f))

    def run(self):
        logging.info(self.cfg.experiment.description)

        for stage in self.cfg.stages:
            logging.info(stage.name)
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
