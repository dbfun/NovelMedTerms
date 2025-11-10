import factory
from factory.alchemy import SQLAlchemyModelFactory

from src.container import container
from src.orm.models import Module


class ModuleFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Module
        sqlalchemy_session_factory = lambda: container.db_session()
        sqlalchemy_session_persistence = "flush"

    name = factory.Sequence(lambda n: f"module_{n}")
