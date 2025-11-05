import logging

import nltk

from src.dictionaries.stop_words import StopWords
from src.modules.module import Module
from src.modules.module_registry import register_module
from src.orm.models import Article, Term


@register_module(module="ner", type="pos-based-hybrid")
class PosBasedHybrid(Module):
    """
    Модуль для извлечения медицинских терминов из аннотаций статей
    с использованием POS-based hybrid подхода.

    Метод основан на анализе частей речи (POS-tagging) и фильтрации
    по стоп-словам для выделения именных групп как терминов.
    """

    MIN_TERM_LENGTH = 3  # Минимальная длина термина в символах

    def __init__(self, stopwords: list = None):
        """
        Инициализация модуля.

        Args:
            stopwords: Список путей к файлам со списками стоп-слов.
        """

        if stopwords is None:
            stopwords = {}

        loader = StopWords(stopwords)

        self.stop_words = loader.load()

    def handle(self) -> None:
        """Извлечение терминов из всех статей в базе данных."""
        from src.container import container

        with container.db_session() as session:
            # Получаем все статьи из БД
            articles = session.query(Article).all()
            logging.info(f"Начало обработки {len(articles)} статей")

            term_count = 0
            processed_count = 0

            for article in articles:
                # Пропускаем статьи без аннотации
                if not article.abstract or len(article.abstract.strip()) == 0:
                    logging.debug(f"Статья {article.id} пропущена: отсутствует abstract")
                    continue

                # Извлекаем термины из аннотации
                terms = self.extract_terms_from_text(article.abstract)

                # Сохраняем термины в БД
                for term_data in terms:
                    term = Term(
                        term_text=term_data["text"],
                        word_count=term_data["word_count"],
                        article_id=article.id,
                        start_char=term_data["start_pos"],
                        end_char=term_data["end_pos"]
                    )
                    session.add(term)
                    term_count += 1

                processed_count += 1

                # Периодический commit для больших объёмов
                if processed_count % 100 == 0:
                    session.commit()
                    logging.info(
                        f"Обработано статей: {processed_count}/{len(articles)}, извлечено терминов: {term_count}")

            # Финальный commit
            session.commit()
            logging.info(f"Обработка завершена. Всего извлечено терминов: {term_count}")

    def extract_terms_from_text(self, text: str) -> list[dict]:
        """
        Извлекает термины из текста.

        Args:
            text: Текст для анализа

        Returns:
            Список словарей с данными о терминах:
            [{"text": str, "word_count": int, "start_pos": int, "end_pos": int}, ...]
        """

        char_pos = 0
        ret = []

        text_len = len(text)
        term = ""
        start_pos = 0
        word_count = 0
        is_term = False  # если в термине есть существительное или герундий, то это термин
        while char_pos < text_len:
            if text[char_pos].isalpha():
                next_word = text[char_pos:].split()[0]
                cleaned_word, end_of_term = self.clean_word(next_word)
                stop_w = False

                if term == "":
                    start_pos = char_pos
                    word_count = 0

                if self.is_term(cleaned_word):  # Надо раньше анализировать!!!
                    term = term + cleaned_word + " "
                    word_count += 1
                else:
                    stop_w = True
                char_pos += len(next_word)  # Позиция следующего символа за словом

                cond1 = char_pos < text_len and text[char_pos] != " " and term != "" and not text[
                    char_pos].isalpha() or stop_w or end_of_term

                cond2 = (char_pos >= text_len) and term != "" or end_of_term or (char_pos < text_len) and term != "" and \
                        text[char_pos] != " " and not text[char_pos].isalpha()

                if cond1 or cond2:
                    if not is_term:
                        is_term = self.is_term(term)
                    if is_term:
                        self.add_term_if_valid(ret, start_pos, term, word_count)
                        term = ""
                        is_term = False
            char_pos += 1

        return ret

    def add_term_if_valid(self, ret: list, start_pos: int, term: str, word_count: int):
        if len(term) > self.MIN_TERM_LENGTH:
            ret.append({"text": term.strip().lower(), "word_count": word_count, "start_pos": start_pos,
                        "end_pos": start_pos + len(term.strip())})

    @staticmethod
    def clean_word(word: str) -> tuple[str, bool]:
        """
        Очищает слово от окружающих символов.

        Args:
            word: Слово для очистки

        Returns:
            Кортеж (слово без окружающих символов, признак "конец термина")
        """
        word = word.strip().lower()
        word_len = len(word)  # длина слова с окружающими символами
        end_of_term = False
        while word_len > 0 and word[0] in '/;(.,!:"':  # Удаление не букв в начале слова
            word = word[1:word_len]
            word_len = word_len - 1
        while word_len > 0 and word[-1] in '/;).,!:"':  # Удаление не букв в конце слова
            word = word[:-1]
            word_len = word_len - 1
            end_of_term = True
        word = word.strip()
        return word, end_of_term

    def is_term(self, term: str) -> bool:
        """
        Проверяет, подходит ли слово для включения в термин.

        Слово подходит, если:
        1. Не является стоп-словом
        2. Содержит существительное (NN), иностранное слово (FW) или герундий (VBG)

        Args:
            term: Слово для проверки

        Returns:
            True, если слово подходит для термина
        """

        if term.lower() in self.stop_words:
            return False

        tokens = nltk.word_tokenize(term)
        tagged = nltk.pos_tag(tokens)

        for tag in tagged:
            # В оригинале была логическая ошибка - стоп-слова не учитывались из-за выражения
            # "or ... or ... and ...".
            # Правильный вариант: "(or ... or ...) and ..."
            # В частности, "case control" попадает в термины.

            if PosBasedHybrid.valid_pos_tag(tag):
                return True
        return False

    @staticmethod
    def valid_pos_tag(tag) -> bool:
        return ("NN" in tag) or ("FW" in tag) or ("VBG" in tag)
