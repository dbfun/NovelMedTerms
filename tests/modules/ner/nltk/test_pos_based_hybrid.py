from unittest.mock import patch

import pytest

from src.modules.ner.pos_based_hybrid import PosBasedHybrid


class TestIsTerm:
    """
    Тесты для метода _is_term.

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
        assert module_missing_stopwords._is_term(word) is True

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
        assert module_missing_stopwords._is_term(word) is False

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
        assert module_with_stopwords._is_term(word) is False

    # Комбинированные случаи
    @patch("nltk.pos_tag")
    @patch("nltk.word_tokenize")
    def test_compound_with_nn_in_middle(self, mock_tokenize, mock_pos_tag, module_missing_stopwords):
        """Если хотя бы одно слово в compound имеет тег NN — считается термином."""
        mock_tokenize.return_value = ["multi", "word"]
        mock_pos_tag.return_value = [("multi", "JJ"), ("word", "NN")]
        assert module_missing_stopwords._is_term("multi-word") is True


class TestCleanWord:
    """TDD тесты для метода _clean_word."""

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
        assert module._clean_word(input_word) == expected


class TestExtractTermsFromText:
    """Тесты для метода _extract_terms_from_text."""

    @pytest.fixture
    def module(self):
        """Фикстура для создания экземпляра модуля."""
        return PosBasedHybrid()

    def test_real_abstract(self, module):
        """Проверка извлечения терминов на примере реальной статьи."""
        text = "OBJECTIVE: We compared the diagnostic values of mammography and magnetic resonance imaging (MRI) for evaluating breast masses. METHODS: We retrospectively analyzed mammography, MRI, and histopathological data for 377 patients with breast masses on mammography, including 73 benign and 304 malignant masses. RESULTS: The sensitivities and negative predictive values (NPVs) were significantly higher for MRI compared with mammography for detecting breast cancer (98.4% vs. 89.8% and 87.8% vs. 46.6%, respectively). The specificity and positive predictive values (PPV) were similar for both techniques. Compared with mammography alone, mammography plus MRI improved the specificity (67.1% vs. 37.0%) and PPV (91.8% vs. 85.6%), but there was no significant difference in sensitivity or NPV. Compared with MRI alone, the combination significantly improved the specificity (67.1% vs. 49.3%), but the sensitivity (88.5% vs. 98.4%) and NPV (58.3% vs. 87.8%) were reduced, and the PPV was similar in both groups. There was no significant difference between mammography and MRI in terms of sensitivity or specificity among 81 patients with breast masses with calcification. CONCLUSION: Breast MRI improved the sensitivity and NPV for breast cancer detection. Combining MRI and mammography improved the specificity and PPV, but MRI offered no advantage in patients with breast masses with calcification."
        expected = [
            {'text': 'objective', 'word_count': 1, 'start_pos': 0, 'end_pos': 9, 'surface_form': 'objective'},
            {'text': 'mammography', 'word_count': 1, 'start_pos': 48, 'end_pos': 59,
             'surface_form': 'mammography'},
            {'text': 'resonance imaging mri', 'word_count': 3, 'start_pos': 73, 'end_pos': 94,
             'surface_form': 'resonance imaging mri'},
            {'text': 'evaluating breast', 'word_count': 2, 'start_pos': 101, 'end_pos': 118,
             'surface_form': 'evaluating breast'},
            {'text': 'mammography', 'word_count': 1, 'start_pos': 164, 'end_pos': 175,
             'surface_form': 'mammography'},
            {'text': 'mri', 'word_count': 1, 'start_pos': 177, 'end_pos': 180, 'surface_form': 'mri'},
            {'text': 'breast', 'word_count': 1, 'start_pos': 231, 'end_pos': 237, 'surface_form': 'breast'},
            {'text': 'mammography', 'word_count': 1, 'start_pos': 248, 'end_pos': 259,
             'surface_form': 'mammography'},
            {'text': 'including benign', 'word_count': 2, 'start_pos': 261, 'end_pos': 277,
             'surface_form': 'including benign'},
            {'text': 'malignant', 'word_count': 1, 'start_pos': 289, 'end_pos': 298,
             'surface_form': 'malignant'},
            {'text': 'predictive', 'word_count': 1, 'start_pos': 347, 'end_pos': 357,
             'surface_form': 'predictive'},
            {'text': 'npvs', 'word_count': 1, 'start_pos': 366, 'end_pos': 370, 'surface_form': 'npvs'},
            {'text': 'mri', 'word_count': 1, 'start_pos': 402, 'end_pos': 405, 'surface_form': 'mri'},
            {'text': 'mammography', 'word_count': 1, 'start_pos': 420, 'end_pos': 431,
             'surface_form': 'mammography'},
            {'text': 'detecting breast cancer vs', 'word_count': 4, 'start_pos': 436, 'end_pos': 462,
             'surface_form': 'detecting breast cancer vs'},
            {'text': 'specificity', 'word_count': 1, 'start_pos': 517, 'end_pos': 528,
             'surface_form': 'specificity'},
            {'text': 'predictive', 'word_count': 1, 'start_pos': 542, 'end_pos': 552,
             'surface_form': 'predictive'},
            {'text': 'ppv', 'word_count': 1, 'start_pos': 561, 'end_pos': 564, 'surface_form': 'ppv'},
            {'text': 'mammography', 'word_count': 1, 'start_pos': 614, 'end_pos': 625,
             'surface_form': 'mammography'},
            {'text': 'mammography', 'word_count': 1, 'start_pos': 633, 'end_pos': 644,
             'surface_form': 'mammography'},
            {'text': 'mri', 'word_count': 1, 'start_pos': 650, 'end_pos': 653, 'surface_form': 'mri'},
            {'text': 'specificity vs', 'word_count': 2, 'start_pos': 667, 'end_pos': 681,
             'surface_form': 'specificity vs'},
            {'text': 'ppv vs', 'word_count': 2, 'start_pos': 701, 'end_pos': 707, 'surface_form': 'ppv vs'},
            {'text': 'difference', 'word_count': 1, 'start_pos': 753, 'end_pos': 763,
             'surface_form': 'difference'},
            {'text': 'sensitivity', 'word_count': 1, 'start_pos': 767, 'end_pos': 778,
             'surface_form': 'sensitivity'},
            {'text': 'npv', 'word_count': 1, 'start_pos': 782, 'end_pos': 785, 'surface_form': 'npv'},
            {'text': 'mri', 'word_count': 1, 'start_pos': 801, 'end_pos': 804, 'surface_form': 'mri'},
            {'text': 'combination', 'word_count': 1, 'start_pos': 816, 'end_pos': 827,
             'surface_form': 'combination'},
            {'text': 'specificity vs', 'word_count': 2, 'start_pos': 855, 'end_pos': 869,
             'surface_form': 'specificity vs'},
            {'text': 'sensitivity vs', 'word_count': 2, 'start_pos': 894, 'end_pos': 908,
             'surface_form': 'sensitivity vs'},
            {'text': 'npv vs', 'word_count': 2, 'start_pos': 928, 'end_pos': 934, 'surface_form': 'npv vs'},
            {'text': 'ppv', 'word_count': 1, 'start_pos': 972, 'end_pos': 975, 'surface_form': 'ppv'},
            {'text': 'difference', 'word_count': 1, 'start_pos': 1029, 'end_pos': 1039,
             'surface_form': 'difference'},
            {'text': 'mammography', 'word_count': 1, 'start_pos': 1048, 'end_pos': 1059,
             'surface_form': 'mammography'},
            {'text': 'mri', 'word_count': 1, 'start_pos': 1064, 'end_pos': 1067, 'surface_form': 'mri'},
            {'text': 'sensitivity', 'word_count': 1, 'start_pos': 1080, 'end_pos': 1091,
             'surface_form': 'sensitivity'},
            {'text': 'specificity', 'word_count': 1, 'start_pos': 1095, 'end_pos': 1106,
             'surface_form': 'specificity'},
            {'text': 'breast', 'word_count': 1, 'start_pos': 1130, 'end_pos': 1136, 'surface_form': 'breast'},
            {'text': 'calcification', 'word_count': 1, 'start_pos': 1149, 'end_pos': 1162,
             'surface_form': 'calcification'},
            {'text': 'conclusion', 'word_count': 1, 'start_pos': 1164, 'end_pos': 1174,
             'surface_form': 'conclusion'},
            {'text': 'breast mri', 'word_count': 2, 'start_pos': 1176, 'end_pos': 1186,
             'surface_form': 'breast mri'},
            {'text': 'sensitivity', 'word_count': 1, 'start_pos': 1200, 'end_pos': 1211,
             'surface_form': 'sensitivity'},
            {'text': 'npv', 'word_count': 1, 'start_pos': 1216, 'end_pos': 1219, 'surface_form': 'npv'},
            {'text': 'breast cancer detection', 'word_count': 3, 'start_pos': 1224, 'end_pos': 1247,
             'surface_form': 'breast cancer detection'},
            {'text': 'combining mri', 'word_count': 2, 'start_pos': 1249, 'end_pos': 1262,
             'surface_form': 'combining mri'},
            {'text': 'mammography', 'word_count': 1, 'start_pos': 1267, 'end_pos': 1278,
             'surface_form': 'mammography'},
            {'text': 'specificity', 'word_count': 1, 'start_pos': 1292, 'end_pos': 1303,
             'surface_form': 'specificity'},
            {'text': 'ppv', 'word_count': 1, 'start_pos': 1308, 'end_pos': 1311, 'surface_form': 'ppv'},
            {'text': 'mri', 'word_count': 1, 'start_pos': 1317, 'end_pos': 1320, 'surface_form': 'mri'},
            {'text': 'advantage', 'word_count': 1, 'start_pos': 1332, 'end_pos': 1341,
             'surface_form': 'advantage'},
            {'text': 'breast', 'word_count': 1, 'start_pos': 1359, 'end_pos': 1365, 'surface_form': 'breast'},
            {'text': 'calcification', 'word_count': 1, 'start_pos': 1378, 'end_pos': 1391,
             'surface_form': 'calcification'}
        ]

        actual = module._extract_terms_from_text(text)

        assert expected == actual
