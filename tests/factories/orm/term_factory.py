import factory
from factory.alchemy import SQLAlchemyModelFactory

from src.container import container
from src.orm.models import Term


class TermFactory(SQLAlchemyModelFactory):
    """
    Фабрика для создания Term

    Документация: https://factoryboy.readthedocs.io/en/stable/orms.html#module-factory.alchemy
    """

    class Meta:
        model = Term
        sqlalchemy_session_factory = lambda: container.db_session()
        sqlalchemy_session_persistence = "flush"

    term_text = factory.Sequence(lambda n: f"term_{n + 1}")
    word_count = 1
    pos_model = "NN"
