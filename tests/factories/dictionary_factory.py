import factory
from factory.alchemy import SQLAlchemyModelFactory

from src.container import container
from src.orm.models import Dictionary


class DictionaryFactory(SQLAlchemyModelFactory):
    """
    Фабрика для создания Dictionary

    Документация: https://factoryboy.readthedocs.io/en/stable/orms.html#module-factory.alchemy
    """

    class Meta:
        model = Dictionary
        sqlalchemy_session_factory = lambda: container.db_session()
        sqlalchemy_session_persistence = "flush"

    name = factory.Sequence(lambda n: f"dict_{n}")
