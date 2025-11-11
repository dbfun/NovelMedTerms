import logging
from pathlib import Path
from typing import Set, List, Union, Any

import nltk
import pandas as pd
from pandas import DataFrame

logger = logging.getLogger("stop-words")


class StopWords:
    """
    Загрузчик стоп-слов из файлов Excel и CSV.

    Поддерживает:
        - Множественные файлы
        - Форматы: .xlsx, .xls, .csv
        - Множественные листы в Excel
        - Автоматическая очистка и нормализация слов
    """

    def __init__(self, file_paths: Union[str, Path, List[Union[str, Path]]] = None):
        """
        Args:
            file_paths: путь (или список) к файлу со стоп-словами
        """
        self.file_paths = self._normalize_paths(file_paths)
        self.stop_words: Set[str] = set()

    def _normalize_paths(self, file_paths: Union[str, Path, List[Union[str, Path]], None]) -> List[Path]:
        """
        Приведение пути (путей) к файлам в формат списка путей.

        Args:
            file_paths: путь (пути) к файлу (файлам)

        Returns:
            Список путей
        """
        if file_paths is None:
            return []

        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]

        return [Path(p) for p in file_paths]

    def load(self) -> Set[str]:
        """
        Получить список стоп-слов из nltk и файлов

        Returns:
            Список стоп-слов
        """
        self.stop_words = set()

        nltk_stopwords = set(nltk.corpus.stopwords.words("english"))
        self.stop_words.update(nltk_stopwords)
        logger.info(f"Загружено {len(nltk_stopwords)} стоп-слов из NLTK")

        # Загружаем стоп-слова из файлов
        for file_path in self.file_paths:
            if not file_path.exists():
                logger.warning(f"Файл не найден: {file_path}")
                continue

            try:
                words = self._load_from_file(file_path)
                self.stop_words.update(words)
                logger.info(f"Загружено {len(words)} стоп-слов из {file_path.name}")
            except Exception as e:
                logger.error(f"Ошибка при загрузке {file_path}: {e}")

        logger.info(f"Всего загружено стоп-слов: {len(self.stop_words)}")
        return self.stop_words

    def _load_from_file(self, file_path: Path) -> Set[str]:
        """
        Загрузить список стоп-слов из файла.

        Args:
            file_path: путь к файлу

        Returns:
            Список стоп-слов
        """
        suffix = file_path.suffix.lower()

        if suffix in [".xlsx", ".xls"]:
            return self._load_from_excel(file_path)
        elif suffix == ".csv":
            return self._load_from_csv(file_path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {suffix}")

    def _load_from_excel(self, file_path: Path) -> Set[str]:
        """
        Загрузить список стоп-слов из Excel-файла.

        Args:
            file_path: путь к файлу

        Returns:
            Список стоп-слов
        """
        words = set()

        # Читаем все листы
        excel_file = pd.ExcelFile(file_path)

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

            self._add_words_from_df(df, words)

        return words

    def _load_from_csv(self, file_path: Path) -> Set[str]:
        """
        Загрузить список стоп-слов из CSV-файла.

        Args:
            file_path: путь к файлу

        Returns:
            Список стоп-слов
        """
        words = set()

        # Читаем CSV без заголовка
        df = pd.read_csv(file_path, header=None)

        self._add_words_from_df(df, words)

        return words

    def _add_words_from_df(self, df: DataFrame, words: set[Any]):
        # Извлекаем слова из первого столбца
        if not df.empty and len(df.columns) > 0:
            # Берем первый столбец, удаляем NaN
            column_words = df.iloc[:, 0].dropna()

            # Обрабатываем каждое слово
            for word in column_words:
                cleaned_word = self._clean_word(str(word))
                if cleaned_word:
                    words.add(cleaned_word)

    def _clean_word(self, word: str) -> str:
        """
        Очистка и нормализация слова.

        Args:
            word: Исходное слово

        Returns:
            Очищенное слово в нижнем регистре
        """
        # Удаляем все символы кроме букв и пробелов
        cleaned = "".join(c for c in word if c.isalpha() or c.isspace())

        # Приводим к нижнему регистру и удаляем лишние пробелы
        return cleaned.lower().strip()

    def __len__(self) -> int:
        """Количество загруженных стоп-слов"""
        return len(self.stop_words)

    def __contains__(self, word: str) -> bool:
        """
        Проверка на стоп-слово

        Args:
            word: слово для проверки

        Returns:
            Признак стоп-слова
        """
        return self._clean_word(word) in self.stop_words
