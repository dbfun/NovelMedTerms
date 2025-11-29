import logging
from abc import abstractmethod

from cachetools import cached, LFUCache
from sqlalchemy.orm import Session

from src.dictionaries.stop_words import StopWords
from src.modules.module import Module
from src.orm.models import Article, ArticleTermAnnotation, Term


class Ner(Module):
    term_id_cache = LFUCache(maxsize=10000)

    @abstractmethod
    def _extract_terms_from_text(self, text: str) -> list[dict]:
        """
        Извлекает термины из текста.

        Args:
            text: текст для анализа

        Returns:
            Список словарей с данными о терминах:
            [{"text": str, "word_count": int, "start_pos": int, "end_pos": int, "surface_form": str}, ...]
        """
        pass

    def __init__(self, stopwords: list = None):
        """
        Инициализация модуля.

        Args:
            stopwords: список путей к файлам со списками стоп-слов.
        """

        self.logger = logging.getLogger(self.info().name())

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
                # Пропускаем статьи без аннотации
                if not article.abstract or len(article.abstract.strip()) == 0:
                    self.logger.debug(f"Статья {article.id} пропущена: отсутствует abstract")
                    continue

                # Извлекаем термины из аннотации
                terms = self._extract_terms_from_text(article.abstract)


                # Сохраняем термины и разметку статей по терминам в БД
                for term_data in terms:
                    term_id = self._get_or_create_term_id(session, term_data)

                    article_term_annotation = ArticleTermAnnotation(
                        term_id=term_id,
                        article_id=article.id,
                        module_id=module_id,
                        start_char=term_data["start_pos"],
                        end_char=term_data["end_pos"],
                        surface_form=term_data["surface_form"],
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

    @cached(cache=term_id_cache, key=lambda self, session, term_data: term_data["text"])
    def _get_or_create_term_id(self, session: Session, term_data: dict) -> int:
        """
        Получить id термина, а если его нет - создать.
        Args:
            session: сессия SQLAlchemy
            term_data: данные о термине

        Returns:
            id термина
        """
        term = session.query(Term).filter_by(term_text=term_data["text"]).first()

        if not term:
            term = Term(term_text=term_data["text"], word_count=term_data["word_count"])
            session.add(term)
            session.flush()

        return term.id
