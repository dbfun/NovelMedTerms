import logging

from src.modules.module import Module
from src.modules.module_registry import register_module
from src.orm import models
from src.orm.database import BaseModel

logger = logging.getLogger("cleaner-database")


@register_module(module="cleaner", type="database")
class CleanerDatabase(Module):

    def __init__(self, models: list):
        self.models = models

    def handle(self):
        from src.container import container

        with container.db_session() as session:
            for model_name in self.models:
                model: BaseModel = getattr(models, model_name)

                logger.info(f"Очистка модели {model_name}")

                session.query(model).delete()
                session.commit()
