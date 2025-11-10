from sqlalchemy.orm.session import Session

from factories import ArticleFactory, ModuleFactory, TermFactory
from factories.article_term_annotation_factory import ArticleTermAnnotationFactory
from src.orm.models import Article


class TestArticleFactory:
    """Тестирование ArticleFactory"""

    def test_build(self, db_session):
        """Проверка создания Article через build"""
        article = ArticleFactory.build()
        db_session.add(article)
        db_session.commit()
        self._assert_stored(db_session)

    def test_create(self, db_session):
        """Проверка создания Article через create"""
        ArticleFactory.create()
        self._assert_stored(db_session)

    def _assert_stored(self, db_session: Session):
        saved_article = db_session.query(Article).first()
        assert saved_article.pmcid.startswith("PMC")


class TestArticleTermAnnotationFactory:
    """Тестирование ArticleTermAnnotationFactory"""

    def test_create(self, db_session):
        annotation = ArticleTermAnnotationFactory.create()
        assert annotation.term.term_text.startswith("term_")


class TestModuleFactory:
    """Тестирование ModuleFactory"""

    def test_create(self, db_session):
        module = ModuleFactory.create()
        assert module.name.startswith("module_")


class TestTermFactory:
    """Тестирование TermFactory"""

    def test_create(self, db_session):
        term = TermFactory.create()
        assert term.term_text.startswith("term_")
        assert term.word_count == 1
