from datetime import date
from unittest.mock import patch

import pytest

from src.modules.module import ModuleInfo
from src.modules.ner.ner import Ner
from src.orm.models import Article, Term, ArticleTermAnnotation


class NerStub(Ner):
    def _extract_terms_from_text(self, text):
        # будет переписано через patch
        return []

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="ner", type="pytest")


class TestNer:
    @pytest.mark.parametrize(
        "term, expected",
        [
            ("calcification", "NN"),
            ("breast cancer", "NN + NN"),
            ("", "")
        ],
    )
    def test_term_pos_model(self, term: str, expected: str) -> None:
        """Проверка метода _term_pos_model"""
        module = NerStub()
        assert expected == module._term_pos_model(term)


class TestHandle:
    """
    Интеграционный тест для метода handle.
    """

    def test_handle_extracts_and_saves_terms(self, db_session):
        """
        Проверяет основной путь:
            1. чтение статей из БД
            2. извлечение терминов
            3. сохранение терминов в БД
            4. сохранение разметки статьи по терминам в БД
        """

        # Подготовка: создаем тестовые статьи
        article1 = Article(
            pmcid="PMC01",
            authors="Test Author",
            title="Test Title",
            abstract="Cancer treatment is effective therapy.",
            pubdate=date(2021, 1, 1)
        )
        article2 = Article(
            pmcid="PMC02",
            authors="Test Author",
            title="Test Title",
            abstract="Cancer treatment for elderly patients living alone.",
            pubdate=date(2021, 1, 1)
        )
        db_session.add_all([article1, article2])
        db_session.commit()

        article_ids = [article1.id, article2.id]

        # Мокаем "_extract_terms_from_text" - будут возвращаться определенные значения.
        term_1 = {
            "text": "cancer treatment",
            "word_count": 2,
            "start_pos": 0,
            "end_pos": 16,
            "surface_form": "Cancer treatment",
            "pos_model": "NN + NN",
        }

        term_2 = {
            "text": "effective therapy",
            "word_count": 2,
            "start_pos": 20,
            "end_pos": 37,
            "surface_form": "effective therapy",
            "pos_model": "NN + NN",
        }

        term_3 = {
            "text": "elderly patients living alone",
            "word_count": 4,
            "start_pos": 21,
            "end_pos": 50,
            "surface_form": "elderly patients living alone",
            "pos_model": "NN + NN + NN + NN",
        }

        module = NerStub()
        with patch.object(module, "_extract_terms_from_text", side_effect=[[term_1, term_2], [term_1, term_3]]):
            # Запуск извлечения терминов
            module.handle()

            # Проверка: термины должны быть сохранены в БД
            term = db_session.query(Term).order_by(Term.id).all()

            assert len(term) == 3, "Термины должны быть извлечены и сохранены"

            assert term[0].term_text == 'cancer treatment'
            assert term[0].word_count == 2
            assert term[0].pos_model == "NN + NN"
            assert term[1].term_text == 'effective therapy'
            assert term[1].word_count == 2
            assert term[1].pos_model == "NN + NN"
            assert term[2].term_text == 'elderly patients living alone'
            assert term[2].word_count == 4
            assert term[2].pos_model == "NN + NN + NN + NN"

            # Проверка: разметка статей по терминам
            article_term_annotations = db_session.query(ArticleTermAnnotation).filter(
                ArticleTermAnnotation.article_id == article_ids[0]).order_by(
                ArticleTermAnnotation.id).all()
            assert len(article_term_annotations) == 2, "Разметка не сохранена"

            assert article_term_annotations[0].start_char == 0
            assert article_term_annotations[0].end_char == 16
            assert article_term_annotations[0].surface_form == 'Cancer treatment'
            assert article_term_annotations[1].start_char == 20
            assert article_term_annotations[1].end_char == 37
            assert article_term_annotations[1].surface_form == 'effective therapy'

            article_term_annotations = db_session.query(ArticleTermAnnotation).filter(
                ArticleTermAnnotation.article_id == article_ids[1]).order_by(
                ArticleTermAnnotation.id).all()
            assert len(article_term_annotations) == 2, "Разметка не сохранена"

            assert article_term_annotations[0].start_char == 0
            assert article_term_annotations[0].end_char == 16
            assert article_term_annotations[0].surface_form == 'Cancer treatment'
            assert article_term_annotations[1].start_char == 21
            assert article_term_annotations[1].end_char == 50
            assert article_term_annotations[1].surface_form == 'elderly patients living alone'
