import nltk

from src.modules.module import ModuleInfo
from src.modules.ner.ner import Ner, TermDto


class PosBasedHybrid(Ner):
    """
    Модуль для извлечения медицинских терминов
    с использованием POS-based hybrid подхода.

    Метод основан на анализе частей речи (POS-tagging) и фильтрации
    по стоп-словам для выделения именных групп как терминов.
    """

    MIN_TERM_LENGTH = 3  # Минимальная длина термина в символах

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="ner", type="pos-based-hybrid")

    def _extract_terms_from_text(self, text: str) -> list[TermDto]:
        char_pos = 0
        ret = []

        text_len = len(text)
        term = ""
        start_pos = 0
        word_count = 0
        term_pos = []
        is_term = False  # если в термине есть существительное или герундий, то это термин
        while char_pos < text_len:
            if text[char_pos].isalpha():
                next_word = text[char_pos:].split()[0]
                cleaned_word, end_of_term = self._clean_word(next_word)
                stop_w = False

                if term == "":
                    start_pos = char_pos
                    word_count = 0
                    term_pos = []

                is_valid, pos_tags = self._is_term(cleaned_word)
                if is_valid:  # Надо раньше анализировать!!!
                    term = term + cleaned_word + " "
                    word_count += len(pos_tags)
                    term_pos += pos_tags
                else:
                    stop_w = True
                char_pos += len(next_word)  # Позиция следующего символа за словом

                cond1 = char_pos < text_len and text[char_pos] != " " and term != "" and not text[
                    char_pos].isalpha() or stop_w or end_of_term

                cond2 = (char_pos >= text_len) and term != "" or end_of_term or (char_pos < text_len) and term != "" and \
                        text[char_pos] != " " and not text[char_pos].isalpha()

                if cond1 or cond2:
                    if not is_term:
                        is_term, pos_tags = self._is_term(term)
                    if is_term:
                        self._add_term_if_valid(ret, start_pos, term, word_count, term_pos)
                        term = ""
                        is_term = False
            char_pos += 1

        return ret

    def _add_term_if_valid(self,
                           ret: list[TermDto],
                           start_pos: int,
                           term: str,
                           word_count: int,
                           term_pos: list) -> None:
        if len(term) > self.MIN_TERM_LENGTH:
            text = term.strip().lower()
            # Прошлая фильтрация по списку стоп-слов работала с отдельными словами.
            # Тут дополнительно фильтруются термины, состоящие из нескольких слов (например, "mean age").
            if text not in self.stop_words:
                dto = TermDto(
                    text=text,
                    word_count=word_count,
                    start_pos=start_pos,
                    end_pos=start_pos + len(term.strip()),
                    surface_form=term.strip(),
                    pos_model=" + ".join(term_pos)
                )
                ret.append(dto)

    @staticmethod
    def _clean_word(word: str) -> tuple[str, bool]:
        """
        Очищает слово от окружающих символов.

        Args:
            word: слово для очистки

        Returns:
            кортеж (слово без окружающих символов, признак "конец термина")
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

    def _is_term(self, term: str) -> tuple[bool, list[str]]:
        """
        Проверяет, подходит ли слово для включения в термин.

        Слово подходит, если:
        1. Не является стоп-словом
        2. Содержит существительное (NN), иностранное слово (FW) или герундий (VBG)

        Args:
            term: слово для проверки

        Returns:
            True, если слово подходит для термина
        """

        if term.lower() in self.stop_words:
            return False, []

        tokens = nltk.word_tokenize(term)
        tagged = nltk.pos_tag(tokens)

        for tag in tagged:
            # В оригинале была логическая ошибка - стоп-слова не учитывались из-за выражения
            # "or ... or ... and ...".
            # Правильный вариант: "(or ... or ...) and ..."
            # В частности, "case control" попадает в термины.

            if PosBasedHybrid._valid_pos_tag(tag):
                pos_tags = [tag for _, tag in tagged]
                return True, pos_tags
        return False, []

    @staticmethod
    def _valid_pos_tag(tag) -> bool:
        # Список тегов: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
        return ("NN" in tag) or ("FW" in tag) or ("VBG" in tag)
