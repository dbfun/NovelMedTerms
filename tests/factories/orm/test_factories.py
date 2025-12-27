from sqlalchemy.orm.session import Session

from factories.orm import ArticleFactory, ModuleFactory, TermFactory, DictionaryFactory, ArticleTermAnnotationFactory, \
    TermDictionaryRefFactory
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
        assert annotation.surface_form.startswith("form_")
        assert annotation.article_field == "abstract"


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
        assert term.pos_model == "NN"
        assert term.label == "Drug"


class TestDictionaryFactory:
    """Тестирование DictionaryFactory"""

    def test_create(self, db_session):
        dictionary = DictionaryFactory.create()
        assert dictionary.name.startswith("dict_")


class TestTermDictionaryRefFactory:
    """Тестирование TermDictionaryRefFactory"""

    def test_create(self, db_session):
        ref = TermDictionaryRefFactory.create()
        assert ref.ref_id.startswith("code_")
