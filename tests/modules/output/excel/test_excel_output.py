from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pandas as pd
import pytest

from factories.orm import TermDictionaryRefFactory, DictionaryFactory, TermFactory, ArticleFactory, \
    ArticleTermAnnotationFactory
from src.modules.output.excel import ExcelOutput
from src.orm.models import Dictionary


class TestExcelOutput:
    @pytest.fixture
    def term_statistics_result(self):
        """Фикстура подсчета статистики"""
        return {
            "Term": "term_in_both",
            "Word count": 1,
            "Year": Decimal("2000"),
            "Count": 1,
            "MeSH": "mesh_code_1",
            "SNOMED CT": "snomed_code_1"
        }

    def test_handle(self, db_session, term_statistics_result):
        """Проверка, что запуск модуля приводит к выполнению цепочки связанных операций"""

        dictionaries = ["MeSH", "SNOMED CT"]
        module = ExcelOutput(dictionaries)

        with patch.object(module, "_load_dictionaries") as mock_load_dicts, \
                patch.object(module, "_load_statistics") as mock_load_stats, \
                patch.object(module, "_generate_excel") as mock_generate:
            # Мокаем параметры
            mesh = DictionaryFactory.build(name="MeSH")
            snomed = DictionaryFactory.build(name="SNOMED CT")

            mock_load_dicts.return_value = [mesh, snomed]
            mock_load_stats.return_value = [term_statistics_result]

            # Запускаем модуль
            module.handle()

            # Проверяем последовательность вызовов
            mock_load_dicts.assert_called_once_with(db_session, dictionaries)
            mock_load_stats.assert_called_once_with(db_session, [mesh, snomed])
            mock_generate.assert_called_once_with([term_statistics_result])

    def test_load_dictionaries(self, db_session):
        """
        Проверка, что метод _load_dictionaries() возвращает список словарей из БД, отфильтрованных
        по названию.
        """
        db_session.add_all([
            TermDictionaryRefFactory.create(),
            TermDictionaryRefFactory.create()
        ])
        db_session.commit()

        assert db_session.query(Dictionary).count() >= 2, "В БД должно быть несколько словарей"

        first_dictionary = db_session.query(Dictionary).first()

        # Запускаем _load_dictionaries()
        module = ExcelOutput([])
        dictionaries = module._load_dictionaries(db_session, [first_dictionary.name])

        assert dictionaries == [first_dictionary], "Выбран не верный словарь"

    def test_load_dictionaries_missing(self, db_session):
        """Проверка, что если передать неверное название словаря, произойдет ошибка"""

        with pytest.raises(RuntimeError) as exc_info:
            module = ExcelOutput([])
            module._load_dictionaries(db_session, ["missing_dictionary"])

        assert "Передан неверный список словарей" in str(exc_info.value)

    def test_load_statistics(self, db_session):
        """
        Проверка _load_statistics на таких входных данных:

            * 2 словаря: MeSH, SNOMED CT.
            * 3 термина:
                * term_in_both - присутствует в обоих словарях;
                * term_in_mesh - только в MeSH;
                * term_not_in_dict - отсутствует в словарях.
            * Несколько статей с разными годами (2000, 2001).
            * Аннотации терминов в статьях для подсчёта count.
            * TermDictionaryRef для связи терминов со словарями.
        """

        # Заполняем БД данными для анализа

        # 1. Словари
        mesh = DictionaryFactory.build(name="MeSH")
        snomed = DictionaryFactory(name="SNOMED CT")
        db_session.add_all([mesh, snomed])
        db_session.commit()

        # 2. Термины
        term_both = TermFactory(term_text="term_in_both")
        term_mesh = TermFactory(term_text="term_in_mesh")
        term_none = TermFactory(term_text="term_not_in_dict")
        db_session.add_all([term_both, term_mesh, term_none])
        db_session.commit()

        # 3. TermDictionaryRef
        TermDictionaryRefFactory(term=term_both, dictionary=mesh, ref_id="mesh_code_1")
        TermDictionaryRefFactory(term=term_both, dictionary=snomed, ref_id="snomed_code_1")
        TermDictionaryRefFactory(term=term_mesh, dictionary=mesh, ref_id="mesh_code_2")
        db_session.commit()

        # 4. Статьи
        article_2000 = ArticleFactory(pubdate=date(2000, 5, 1))
        article_2001 = ArticleFactory(pubdate=date(2001, 7, 1))
        db_session.add_all([article_2000, article_2001])
        db_session.commit()

        # 5. Аннотации
        ArticleTermAnnotationFactory(article=article_2000, term=term_both)
        ArticleTermAnnotationFactory(article=article_2000, term=term_mesh)
        ArticleTermAnnotationFactory(article=article_2001, term=term_both)
        ArticleTermAnnotationFactory(article=article_2001, term=term_none)
        db_session.commit()

        # Получаем результаты
        module = ExcelOutput([])
        statistics = module._load_statistics(db_session, [mesh, snomed])

        # Сравниваем с ожидаемыми данными
        expected = [
            {"Term": "term_in_both", "Word count": 1, "Year": Decimal("2000"), "Count": 1, "MeSH": "mesh_code_1",
             "SNOMED CT": "snomed_code_1"},
            {"Term": "term_in_both", "Word count": 1, "Year": Decimal("2001"), "Count": 1, "MeSH": "mesh_code_1",
             "SNOMED CT": "snomed_code_1"},
            {"Term": "term_in_mesh", "Word count": 1, "Year": Decimal("2000"), "Count": 1, "MeSH": "mesh_code_2",
             "SNOMED CT": ""},
            {"Term": "term_not_in_dict", "Word count": 1, "Year": Decimal("2001"), "Count": 1, "MeSH": "",
             "SNOMED CT": ""}
        ]

        assert statistics == expected

    def test_generate_excel(self, fake_experiment, term_statistics_result):
        """Проверка, что результаты сохранятся в Excel-файл"""

        # Запускаем _generate_excel с фикстурой
        module = ExcelOutput([])
        module.experiment = fake_experiment
        module._generate_excel([term_statistics_result])

        # Проверка наличия файла
        excel_file = module._generate_output_file_path("statistics.xlsx")
        assert excel_file.exists(), "Excel файл не найден"

        # Проверка структуры файла
        df = pd.read_excel(excel_file)
        assert ["Term", "Word count", "Year", "Count", "MeSH",
                "SNOMED CT"] == df.columns.values.tolist(), "Структура не совпадает"

        # Проверка данных
        expected = [
            term_statistics_result["Term"],
            term_statistics_result["Word count"],
            term_statistics_result["Year"],
            term_statistics_result["Count"],
            term_statistics_result["MeSH"],
            term_statistics_result["SNOMED CT"],
        ]
        assert expected == df.values[0].tolist()
