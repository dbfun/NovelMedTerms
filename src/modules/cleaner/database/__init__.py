import logging

from src.modules.module import Module, ModuleInfo
from src.orm import models
from src.orm.database import BaseModel


class CleanerDatabase(Module):

    def __init__(self, models: list):
        self.logger = logging.getLogger(CleanerDatabase.info().name())
        self.models = models

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="cleaner", type="database")

    def handle(self):
        from src.container import container

        with container.db_session() as session:
            for model_name in self.models:
                model: BaseModel = getattr(models, model_name)

                self.logger.info(f"Очистка модели {model_name}")

                session.query(model).delete()
                session.commit()
