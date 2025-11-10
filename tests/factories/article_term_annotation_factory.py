import factory
from factory.alchemy import SQLAlchemyModelFactory

from factories import TermFactory, ArticleFactory, ModuleFactory
from src.container import container
from src.orm.models import ArticleTermAnnotation


class ArticleTermAnnotationFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ArticleTermAnnotation
        sqlalchemy_session_factory = lambda: container.db_session()
        sqlalchemy_session_persistence = "flush"

    term = factory.SubFactory(TermFactory)
    article = factory.SubFactory(ArticleFactory)
    module = factory.SubFactory(ModuleFactory)
    start_char = 0
    end_char = 5
