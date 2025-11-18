import factory
from factory.alchemy import SQLAlchemyModelFactory

from factories import TermFactory, DictionaryFactory
from src.container import container
from src.orm.models import TermDictionaryRef


class TermDictionaryRefFactory(SQLAlchemyModelFactory):
    """
    Фабрика для создания TermDictionaryRef

    Документация: https://factoryboy.readthedocs.io/en/stable/orms.html#module-factory.alchemy
    """

    class Meta:
        model = TermDictionaryRef
        sqlalchemy_session_factory = lambda: container.db_session()
        sqlalchemy_session_persistence = "flush"

    ref_id = factory.Sequence(lambda n: f"code_{n + 1}")
    term = factory.SubFactory(TermFactory)
    dictionary = factory.SubFactory(DictionaryFactory)
