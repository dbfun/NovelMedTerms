from unittest.mock import patch

import pytest

from factories.article_term_annotation_factory import ArticleTermAnnotationFactory
from src.modules.dictionary.mesh import DictionaryMesh, TermDTO, MeSH
from src.orm.models import Term, TermDictionaryRef


class TestDictionaryMesh:

    @pytest.mark.parametrize(
        "search_value, expected_count",
        [
            (TermDTO(ref_id="pytest"), 1),
            (None, 0),
        ],
    )
    def test_handle(self, db_session, search_value, expected_count):
        """Проверка, что модуль при нахождении термина в словаре создает запись в БД"""

        with patch("src.modules.dictionary.mesh.MeSH.search", return_value=search_value):
            ArticleTermAnnotationFactory.create()

            module = DictionaryMesh()
            module.handle()

            term = db_session.query(Term).first()
            assert len(term.dictionaries) == expected_count

            if expected_count:
                assert search_value.ref_id == db_session.query(TermDictionaryRef).first().ref_id


class TestMeSH:
    @pytest.mark.parametrize(
        "search_term, expected_result",
        [
            ("unknown term", None),
            ("MYOCARDIAL INFARCTION", TermDTO(ref_id="D009203")),
            ("heart attack", TermDTO(ref_id="D009203")),
            ("calcification", TermDTO(ref_id="D002113")),
            ("risk", TermDTO(ref_id="D012306")),
            ("breast cancer", TermDTO(ref_id="D000072656")),
        ],
    )
    def test_search(self, search_term, expected_result):
        """Тестирование механизма поиска в базе MeSH"""
        dictionary = MeSH()
        result = dictionary.search(search_term)
        assert result == expected_result
