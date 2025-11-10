import factory
from factory.alchemy import SQLAlchemyModelFactory

from src.container import container
from src.orm.models import Term


class TermFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Term
        sqlalchemy_session_factory = lambda: container.db_session()
        sqlalchemy_session_persistence = "flush"

    term_text = factory.Sequence(lambda n: f"term_{n}")
    word_count = 1
