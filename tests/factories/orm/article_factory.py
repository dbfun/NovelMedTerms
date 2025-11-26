from datetime import date

import factory
from factory.alchemy import SQLAlchemyModelFactory

from src.container import container
from src.orm.models import Article


class ArticleFactory(SQLAlchemyModelFactory):
    """
    Фабрика для создания Article

    Документация: https://factoryboy.readthedocs.io/en/stable/orms.html#module-factory.alchemy
    """

    class Meta:
        model = Article
        sqlalchemy_session_factory = lambda: container.db_session()
        sqlalchemy_session_persistence = "flush"

    pmcid = factory.Sequence(lambda n: f"PMC{10000 + n}")
    authors = factory.Faker("name")
    title = factory.Faker("sentence")
    abstract = factory.Faker("text")
    pubdate = factory.LazyFunction(date.today)
