from datetime import date
from unittest.mock import patch

import pytest

from src.container import container
from src.modules.ner.pos_based_hybrid import PosBasedHybrid
from src.orm.models import Article, Term, TermMarkup


class TestIsTerm:
    """
    Тесты для метода is_term.

    Примечание: мы мокаем nltk.pos_tag() вместо использования реального NLTK,
    потому что POS-tagging зависит от контекста и может давать разные результаты
    для одного и того же слова. Моки обеспечивают предсказуемость и стабильность тестов,
    а также ускоряют их выполнение (не нужно загружать модели NLTK).
    """

    STOP_WORD = "capacity"

    @pytest.fixture
    def module_missing_stopwords(self):
        """Модуль без стоп-слов."""
        module = PosBasedHybrid()
        module.stop_words = {}
        return module

    @pytest.fixture
    def module_with_stopwords(self):
        """Модуль со стоп-словами."""
        module = PosBasedHybrid()
        module.stop_words = {self.STOP_WORD}
        return module

    @staticmethod
    def mock_pos(mock_tokenize, mock_pos_tag, word, tag):
        """Метод для моков nltk.word_tokenize() и nltk.pos_tag()."""
        mock_tokenize.return_value = [word] if word else []
        mock_pos_tag.return_value = [(word, tag)] if word else []

    # Позитивные случаи (термины)
    @pytest.mark.parametrize("word,tag", [
        ("cancer", "NN"),  # существительное, ед. число
        ("learning", "VBG"),  # глагол, герундий/настоящее причастие
        ("diabetes", "FW"),  # иностранное слово
    ])
    @patch("nltk.pos_tag")
    @patch("nltk.word_tokenize")
    def test_positive_cases(self, mock_tokenize, mock_pos_tag, module_missing_stopwords, word, tag):
        """Слова с допустимыми POS-тегами считаются терминами."""
        TestIsTerm.mock_pos(mock_tokenize, mock_pos_tag, word, tag)
        assert module_missing_stopwords.is_term(word) is True

    # Негативные случаи (не термин)
    @pytest.mark.parametrize("word,tag", [
        ("quickly", "RB"),  # наречие
        ("run", "VB"),  # глагол
        ("red", "JJ"),  # прилагательное
        ("walked", "VBD"),  # прошедшее время
        ("in", "IN"),  # предлог
        ("", ""),  # пустая строка
        ("123", "CD"),  # цифры
    ])
    @patch("nltk.pos_tag")
    @patch("nltk.word_tokenize")
    def test_negative_cases(self, mock_tokenize, mock_pos_tag, module_missing_stopwords, word, tag):
        """Слова с недопустимыми POS-тегами не считаются терминами."""
        TestIsTerm.mock_pos(mock_tokenize, mock_pos_tag, word, tag)
        assert module_missing_stopwords.is_term(word) is False

    # Стоп-слова
    @pytest.mark.parametrize("word,tag", [
        (STOP_WORD, "NN"),
        (STOP_WORD.upper(), "NN"),
    ])
    @patch("nltk.pos_tag")
    @patch("nltk.word_tokenize")
    def test_stopwords(self, mock_tokenize, mock_pos_tag, module_with_stopwords, word, tag):
        """Стоп-слова не считаются терминами независимо от регистра."""
        TestIsTerm.mock_pos(mock_tokenize, mock_pos_tag, word, tag)
        assert module_with_stopwords.is_term(word) is False

    # Комбинированные случаи
    @patch("nltk.pos_tag")
    @patch("nltk.word_tokenize")
    def test_compound_with_nn_in_middle(self, mock_tokenize, mock_pos_tag, module_missing_stopwords):
        """Если хотя бы одно слово в compound имеет тег NN — считается термином."""
        mock_tokenize.return_value = ["multi", "word"]
        mock_pos_tag.return_value = [("multi", "JJ"), ("word", "NN")]
        assert module_missing_stopwords.is_term("multi-word") is True


class TestCleanWord:
    """TDD тесты для метода clean_word."""

    @pytest.fixture
    def module(self):
        return PosBasedHybrid()

    @pytest.mark.parametrize(
        "input_word,expected",
        [
            # --- Базовые случаи ---
            ("word", ("word", False)),
            ("hello", ("hello", False)),

            # --- Символы в начале ---
            ("/word", ("word", False)),
            (";:word", ("word", False)),
            (";word", ("word", False)),
            (",word", ("word", False)),

            # --- Символы в конце ---
            ("word.", ("word", True)),
            ("word),", ("word", True)),
            ("word;", ("word", True)),
            ("word!", ("word", True)),
            ("word)", ("word", True)),

            # --- Символы с двух сторон ---
            ("/word.", ("word", True)),
            (";hello!", ("hello", True)),
            ('":medical."', ("medical", True)),

            # --- Пробелы в конце ---
            ("word ", ("word", False)),
            ("word  ", ("word", False)),
            ("word\t", ("word", False)),

            # --- Комбинации ---
            ("/word. ", ("word", True)),
            (";:hello!; ", ("hello", True)),

            # --- Пустые и крайние случаи ---
            ("", ("", False)),
            ("/:;", ("", False)),
            (".!)", ("", True)),
            ("a", ("a", False)),
            ("a.", ("a", True)),

            # --- Медицинские примеры ---
            ("COVID-19.", ("covid-19", True)),
            ('"diabetes"', ("diabetes", True)),
            ("(treatment)", ("treatment", True)),

            # --- Пробелы и переводы строк ---
            ("   ", ("", False)),
            ("word\n", ("word", False)),
        ],
    )
    def test_clean_word_various_cases(self, module, input_word, expected):
        """Проверяет корректность очистки слова в разных сценариях."""
        assert module.clean_word(input_word) == expected


class TestExtractTermsFromText:
    """Тесты для метода extract_terms_from_text."""

    @pytest.fixture
    def module(self):
        """Фикстура для создания экземпляра модуля."""
        return PosBasedHybrid()

    def test_real_abstract(self, module):
        """Проверка извлечения терминов на примере реальной статьи."""
        text = "OBJECTIVE: We compared the diagnostic values of mammography and magnetic resonance imaging (MRI) for evaluating breast masses. METHODS: We retrospectively analyzed mammography, MRI, and histopathological data for 377 patients with breast masses on mammography, including 73 benign and 304 malignant masses. RESULTS: The sensitivities and negative predictive values (NPVs) were significantly higher for MRI compared with mammography for detecting breast cancer (98.4% vs. 89.8% and 87.8% vs. 46.6%, respectively). The specificity and positive predictive values (PPV) were similar for both techniques. Compared with mammography alone, mammography plus MRI improved the specificity (67.1% vs. 37.0%) and PPV (91.8% vs. 85.6%), but there was no significant difference in sensitivity or NPV. Compared with MRI alone, the combination significantly improved the specificity (67.1% vs. 49.3%), but the sensitivity (88.5% vs. 98.4%) and NPV (58.3% vs. 87.8%) were reduced, and the PPV was similar in both groups. There was no significant difference between mammography and MRI in terms of sensitivity or specificity among 81 patients with breast masses with calcification. CONCLUSION: Breast MRI improved the sensitivity and NPV for breast cancer detection. Combining MRI and mammography improved the specificity and PPV, but MRI offered no advantage in patients with breast masses with calcification."
        expected = [
            {"text": "objective", "word_count": 1, "start_pos": 0, "end_pos": 9},
            {"text": "mammography", "word_count": 1, "start_pos": 48, "end_pos": 59},
            {"text": "resonance imaging mri", "word_count": 3, "start_pos": 73, "end_pos": 94},
            {"text": "evaluating breast", "word_count": 2, "start_pos": 101, "end_pos": 118},
            {"text": "mammography", "word_count": 1, "start_pos": 164, "end_pos": 175},
            {"text": "mri", "word_count": 1, "start_pos": 177, "end_pos": 180},
            {"text": "breast", "word_count": 1, "start_pos": 231, "end_pos": 237},
            {"text": "mammography", "word_count": 1, "start_pos": 248, "end_pos": 259},
            {"text": "including benign", "word_count": 2, "start_pos": 261, "end_pos": 277},
            {"text": "malignant", "word_count": 1, "start_pos": 289, "end_pos": 298},
            {"text": "predictive", "word_count": 1, "start_pos": 347, "end_pos": 357},
            {"text": "npvs", "word_count": 1, "start_pos": 366, "end_pos": 370},
            {"text": "mri", "word_count": 1, "start_pos": 402, "end_pos": 405},
            {"text": "mammography", "word_count": 1, "start_pos": 420, "end_pos": 431},
            {"text": "detecting breast cancer vs", "word_count": 4, "start_pos": 436, "end_pos": 462},
            {"text": "specificity", "word_count": 1, "start_pos": 517, "end_pos": 528},
            {"text": "predictive", "word_count": 1, "start_pos": 542, "end_pos": 552},
            {"text": "ppv", "word_count": 1, "start_pos": 561, "end_pos": 564},
            {"text": "mammography", "word_count": 1, "start_pos": 614, "end_pos": 625},
            {"text": "mammography", "word_count": 1, "start_pos": 633, "end_pos": 644},
            {"text": "mri", "word_count": 1, "start_pos": 650, "end_pos": 653},
            {"text": "specificity vs", "word_count": 2, "start_pos": 667, "end_pos": 681},
            {"text": "ppv vs", "word_count": 2, "start_pos": 701, "end_pos": 707},
            {"text": "difference", "word_count": 1, "start_pos": 753, "end_pos": 763},
            {"text": "sensitivity", "word_count": 1, "start_pos": 767, "end_pos": 778},
            {"text": "npv", "word_count": 1, "start_pos": 782, "end_pos": 785},
            {"text": "mri", "word_count": 1, "start_pos": 801, "end_pos": 804},
            {"text": "combination", "word_count": 1, "start_pos": 816, "end_pos": 827},
            {"text": "specificity vs", "word_count": 2, "start_pos": 855, "end_pos": 869},
            {"text": "sensitivity vs", "word_count": 2, "start_pos": 894, "end_pos": 908},
            {"text": "npv vs", "word_count": 2, "start_pos": 928, "end_pos": 934},
            {"text": "ppv", "word_count": 1, "start_pos": 972, "end_pos": 975},
            {"text": "difference", "word_count": 1, "start_pos": 1029, "end_pos": 1039},
            {"text": "mammography", "word_count": 1, "start_pos": 1048, "end_pos": 1059},
            {"text": "mri", "word_count": 1, "start_pos": 1064, "end_pos": 1067},
            {"text": "sensitivity", "word_count": 1, "start_pos": 1080, "end_pos": 1091},
            {"text": "specificity", "word_count": 1, "start_pos": 1095, "end_pos": 1106},
            {"text": "breast", "word_count": 1, "start_pos": 1130, "end_pos": 1136},
            {"text": "calcification", "word_count": 1, "start_pos": 1149, "end_pos": 1162},
            {"text": "conclusion", "word_count": 1, "start_pos": 1164, "end_pos": 1174},
            {"text": "breast mri", "word_count": 2, "start_pos": 1176, "end_pos": 1186},
            {"text": "sensitivity", "word_count": 1, "start_pos": 1200, "end_pos": 1211},
            {"text": "npv", "word_count": 1, "start_pos": 1216, "end_pos": 1219},
            {"text": "breast cancer detection", "word_count": 3, "start_pos": 1224, "end_pos": 1247},
            {"text": "combining mri", "word_count": 2, "start_pos": 1249, "end_pos": 1262},
            {"text": "mammography", "word_count": 1, "start_pos": 1267, "end_pos": 1278},
            {"text": "specificity", "word_count": 1, "start_pos": 1292, "end_pos": 1303},
            {"text": "ppv", "word_count": 1, "start_pos": 1308, "end_pos": 1311},
            {"text": "mri", "word_count": 1, "start_pos": 1317, "end_pos": 1320},
            {"text": "advantage", "word_count": 1, "start_pos": 1332, "end_pos": 1341},
            {"text": "breast", "word_count": 1, "start_pos": 1359, "end_pos": 1365},
            {"text": "calcification", "word_count": 1, "start_pos": 1378, "end_pos": 1391}
        ]

        actual = module.extract_terms_from_text(text)

        assert expected == actual


class TestHandle:
    """
    Интеграционный тест для метода handle.

    Проверяет основной путь:
        1. чтение статей из БД
        2. извлечение терминов
        3. сохранение терминов в БД
        4. сохранение разметки статьи по терминам в БД
    """

    @pytest.fixture
    def module(self):
        """Фикстура для создания экземпляра модуля."""
        return PosBasedHybrid()

    @patch("nltk.pos_tag")
    @patch("nltk.word_tokenize")
    def test_handle_extracts_and_saves_terms(self, mock_tokenize, mock_pos_tag, module):
        """
        Основной путь: handle должен прочитать статьи, извлечь термины и сохранить их в БД.
        """

        # Мокаем NLTK: все слова - существительные (термины)
        mock_tokenize.side_effect = lambda w: [w]
        mock_pos_tag.side_effect = lambda tokens: [(t, "NN") for t in tokens]

        with container.db_session() as session:
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
            session.add_all([article1, article2])
            session.commit()

            article_ids = [article1.id, article2.id]

            # Запуск извлечения терминов
            module.handle()

            # Проверка: термины должны быть сохранены в БД
            term = session.query(Term).order_by(Term.id).all()
            assert len(term) == 3, "Термины должны быть извлечены и сохранены"

            assert term[0].term_text == 'cancer treatment'
            assert term[0].word_count == 2
            assert term[1].term_text == 'effective therapy'
            assert term[1].word_count == 2
            assert term[2].term_text == 'elderly patients living alone'
            assert term[2].word_count == 4

            # Проверка: разметка статей по терминам
            term_markups = session.query(TermMarkup).filter(TermMarkup.article_id == article_ids[0]).order_by(
                TermMarkup.id).all()
            assert len(term_markups) == 2, "Разметка не сохранена"

            assert term_markups[0].start_char == 0
            assert term_markups[0].end_char == 16
            assert term_markups[1].start_char == 20
            assert term_markups[1].end_char == 37

            term_markups = session.query(TermMarkup).filter(TermMarkup.article_id == article_ids[1]).order_by(
                TermMarkup.id).all()
            assert len(term_markups) == 2, "Разметка не сохранена"

            assert term_markups[0].start_char == 0
            assert term_markups[0].end_char == 16
            assert term_markups[1].start_char == 21
            assert term_markups[1].end_char == 50
