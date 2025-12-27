from abc import ABC
from typing import List

import spacy

from src.modules.ner.ner import Ner


class TermFeature:
    def __init__(self, lemmas_parts: List[str], pos_parts: List[str]):
        self.lemmas_parts = lemmas_parts
        self.pos_parts = pos_parts

        self.lemmas = ''.join(lemmas_parts).strip().lower()
        self.pos_model = '+'.join(pos_parts)
        self.word_count = len(pos_parts)


class Transformer(Ner, ABC):
    MIN_TERM_LENGTH = 3  # Минимальная длина термина в символах

    def __init__(self, article_fields: list, stopwords: list = None):
        """
        Инициализация модуля.

        Args:
            article_fields: список полей из статьи для извлечения именованных сущностей.
            stopwords: список путей к файлам со списками стоп-слов.
        """
        super().__init__(article_fields, stopwords)
        self.nlp_en_core_web_sm = spacy.load('en_core_web_sm')
        self.bad_parts = ['PUNCT', 'SYM', 'NUM']

    def _term_feature(self, term: str) -> TermFeature:
        """
        Лемматизация, подсчет количества слов и POS-модель

        Args:
            term: термин

        Returns: лемматизированная форма, количество слов, POS-модель
        """

        doc = self.nlp_en_core_web_sm(term)

        lemmas_parts = []
        pos_parts = []

        i = 0
        while i < len(doc):
            token = doc[i]

            # Проверяем, есть ли следующий токен и является ли он дефисом
            if i + 1 < len(doc) and doc[i + 1].text == '-':
                # Объединяем токены через дефис
                combined_lemma = token.lemma_
                combined_pos = token.pos_  # Берем POS первого токена

                # Пропускаем дефис и добавляем следующие токены
                j = i + 1
                while j < len(doc) and (doc[j].text == '-' or (j > i + 1 and doc[j - 1].text == '-')):
                    if doc[j].text != '-':
                        combined_lemma += '-' + doc[j].lemma_
                    j += 1

                # Добавляем пробел после объединенного слова, если он есть
                if j < len(doc):
                    combined_lemma += doc[j - 1].whitespace_

                lemmas_parts.append(combined_lemma)
                pos_parts.append(combined_pos)

                # Переходим к следующему токену после составного слова
                i = j
            else:
                # Обычный токен (не пунктуация-дефис)
                if token.pos_ != 'PUNCT' or token.text != '-':
                    lemmas_parts.append(
                        token.lemma_ + token.whitespace_ if token.pos_ != 'PUNCT' else token.text + token.whitespace_)
                    pos_parts.append(token.pos_)
                i += 1

        return TermFeature(lemmas_parts, pos_parts)

    def _should_skip(self, term_feature: TermFeature) -> bool:
        # После лемматизации термин может поменяться, проверяем еще раз
        if term_feature.lemmas in self.stop_words:
            return True

        # Пропуск, если не получилось сделать лемматизацию
        if not term_feature.lemmas:
            return True

        # Пропуск, если просто "номер"
        if term_feature.pos_model in ['NUM', 'NUM+NUM', 'NUM+NUM+NUM', 'NUM+NUM+NUM+NUM']:
            return True

        # Пропуск, если много PUNCT, SYM, NUM
        bad_parts_count = sum(1 for p in term_feature.pos_parts if p in self.bad_parts)
        bad_parts_proportion = bad_parts_count / len(term_feature.pos_parts)
        if bad_parts_proportion > 0.5:
            return True

        # Пропуск, если термин слишком короткий
        if len(term_feature.lemmas) < self.MIN_TERM_LENGTH:
            return True

        return False
