from unittest.mock import patch

import pytest

from factories.orm import ArticleTermAnnotationFactory
from src.modules.dictionary import TermDTO
from src.modules.dictionary.snomed import DictionarySnomed, Snomed
from src.orm.models import Term, TermDictionaryRef


class TestDictionarySnomed:

    @pytest.mark.parametrize(
        "search_value, expected_count",
        [
            (TermDTO(ref_id="pytest"), 1),
            (None, 0),
        ],
    )
    def test_handle(self, db_session, search_value, expected_count):
        """Проверка, что модуль при нахождении термина в словаре создает запись в БД"""

        with patch("src.modules.dictionary.snomed.Snomed.search", return_value=search_value):
            ArticleTermAnnotationFactory.create()

            module = DictionarySnomed()
            module.handle()

            term = db_session.query(Term).first()
            assert len(term.dictionaries) == expected_count

            if expected_count:
                assert search_value.ref_id == db_session.query(TermDictionaryRef).first().ref_id


class TestSnomed:
    @pytest.mark.parametrize(
        "search_term, expected_result",
        [
            ("wrong term", None),
            ("MYOCARDIAL INFARCTION", TermDTO(ref_id="22298006")),
        ],
    )
    def test_search(self, search_term, expected_result):
        """Тестирование механизма поиска в базе SNOMED CT"""
        dictionary = Snomed()
        result = dictionary.search(search_term)
        assert result == expected_result
