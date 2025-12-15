import logging
from abc import abstractmethod
from typing import Optional

from cachetools import cached, LFUCache
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.dictionaries.stop_words import StopWords
from src.modules.module import Module
from src.orm.models import Article, ArticleTermAnnotation, Term


class TermDto(BaseModel):
    """DTO с информацией об извлеченном термине"""
    text: str
    word_count: int
    start_pos: int
    end_pos: int
    surface_form: str
    pos_model: str
    article_field: Optional[str] = None


class Ner(Module):
    term_id_cache = LFUCache(maxsize=10000)

    def _extract_terms_from_article_field(self, article: Article, field: str) -> list[TermDto]:
        text = article.get_text(field)
        dto_list = self._extract_terms_from_text(text)
        for dto in dto_list:
            dto.article_field = field
        return dto_list

    @abstractmethod
    def _extract_terms_from_text(self, text: str) -> list[TermDto]:
        """
        Извлекает термины из текста.

        Args:
            text: текст для анализа

        Returns:
            Список словарей с данными о терминах:
            TermDto(text: str, word_count: int, start_pos: int, end_pos: int, surface_form: str, "os_model: str}, ...)
        """
        pass

    def __init__(self, article_fields: list, stopwords: list = None):
        """
        Инициализация модуля.

        Args:
            article_fields: список полей из статьи для извлечения именованных сущностей.
            stopwords: список путей к файлам со списками стоп-слов.
        """

        self.logger = logging.getLogger(self.info().name())

        # Список полей
        if not article_fields:
            raise ValueError("Список полей не может быть пустым")
        self.article_fields = article_fields

        # Загрузка списка стоп-слов
        if stopwords is None:
            stopwords = {}
        loader = StopWords(stopwords)
        self.stop_words = loader.load()

    def handle(self) -> None:
        """Извлечение терминов из всех статей в базе данных."""
        from src.container import container

        with container.db_session() as session:
            module_id = self._register_module_in_db(session)

            # Получаем все статьи из БД
            articles = session.query(Article).all()
            self.logger.info(f"Найдено статей: {len(articles)}")

            term_count = 0
            processed_count = 0

            for article in articles:
                terms = self._extract_terms(article)
                if not terms:
                    self.logger.debug(f"Статья {article.id} пропущена: отсутствует текст")
                    continue

                # Сохраняем термины и разметку статей по терминам в БД
                term_dto: TermDto
                for term_dto in terms:
                    term_id = self._get_or_create_term_id(session, term_dto)

                    article_term_annotation = ArticleTermAnnotation(
                        term_id=term_id,
                        article_id=article.id,
                        module_id=module_id,
                        start_char=term_dto.start_pos,
                        end_char=term_dto.end_pos,
                        surface_form=term_dto.surface_form,
                        article_field=term_dto.article_field,
                    )
                    session.add(article_term_annotation)
                    term_count += 1

                processed_count += 1

                # Периодический commit для больших объемов
                if processed_count % 100 == 0:
                    session.commit()
                    self.logger.debug(
                        f"Обработано статей: {processed_count} из {len(articles)}, извлечено терминов: {term_count}")

            # Финальный commit
            if processed_count % 100 != 0:
                session.commit()
                self.logger.debug(
                    f"Обработано статей: {processed_count} из {len(articles)}, извлечено терминов: {term_count}")

            self.logger.info(f"Обработка завершена. Всего извлечено терминов: {term_count}")

    def _extract_terms(self, article: Article) -> list[TermDto]:
        """
        Извлечение терминов из переданных полей (title, abstract)

        Args:
            article: статья

        Returns:
            Список словарей с данными о терминах.
        """

        terms = []

        field: str
        for field in self.article_fields:
            terms += self._extract_terms_from_article_field(article, field)
        return terms

    @cached(cache=term_id_cache, key=lambda self, session, term_dto: term_dto.text)
    def _get_or_create_term_id(self, session: Session, term_dto: TermDto) -> int:
        """
        Получить id термина, а если его нет - создать.
        Args:
            session: сессия SQLAlchemy
            term_dto: данные о термине

        Returns:
            id термина
        """
        term = session.query(Term).filter_by(term_text=term_dto.text).first()

        if not term:
            term = Term(term_text=term_dto.text,
                        word_count=term_dto.word_count,
                        pos_model=term_dto.pos_model
                        )
            session.add(term)
            session.flush()

        return term.id
