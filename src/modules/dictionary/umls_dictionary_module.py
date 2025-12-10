import logging
from abc import abstractmethod
from sqlite3 import OperationalError

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm.session import Session

from src.modules.dictionary import UmlsMetathesaurus, TermDTO
from src.modules.module import Module
from src.orm.models import Dictionary, TermDictionaryRef, Term


class UmlsDictionaryModule(Module):

    def __init__(self):
        self.logger = logging.getLogger(self.info().name())

    @abstractmethod
    def dictionary(self) -> UmlsMetathesaurus:
        """
        Returns:
            Словарь типа UmlsMetathesaurus, в котором происходит поиск
        """
        pass

    def handle(self) -> None:
        """Запуск поиска"""
        from src.container import container

        known_cnt = 0
        unknown_cnt = 0

        with container.db_session() as session:
            dictionary = self.dictionary()

            dictionary_id = self._register_dictionary_in_db(session, dictionary)

            # Получаем все статьи из БД
            terms = session.query(Term).all()

            # Эта часть работает медленно из-за dictionary.search(). Эта операция занимает ~ 93% времени.
            # На 23066 терминах этап поиска в словаре MeSH выполняется 130-160 сек, загрузка CPU ~100% (один процесс).
            # Было сделано профилирование и визуализация (открывается в браузере):
            #   python -m cProfile -o prof.out workflow.py workflows/simple-dimple.yaml
            #   snakeviz prof.out
            # Установка snakeviz:
            #   sudo apt install pipx
            #   pipx ensurepath
            #   pipx install snakeviz
            # Далее была попытка сделать поиск параллельным за счет multiprocessing. Однако это не удалось сделать
            # из-за блокировки БД воркерами. Была ошибка: "sqlite3.OperationalError: database is locked".
            # Единственный вариант - сделать копии БД для каждого воркера, что накладно по месту на SSD.
            for term in terms:
                try:
                    # Узкое место производительности
                    result = dictionary.search(term.term_text)
                    if result is not None:
                        self._mark_term_as_known(session, dictionary_id, term.id, result)
                        known_cnt += 1
                        self.logger.debug(f"Найдено в словаре: '{term.term_text}'")
                    else:
                        unknown_cnt += 1
                        self.logger.debug(f"Не найдено в словаре: '{term.term_text}'")
                except OperationalError as e:
                    self.logger.error(f"Ошибка поиска: '{term.term_text}'")
                    pass

            session.commit()

        self.logger.info(f"Обработка завершена. Найдено в словаре: {known_cnt}. Не найдено в словаре: {unknown_cnt}")

    def _register_dictionary_in_db(self, session: Session, dictionary: UmlsMetathesaurus) -> int:
        """
        Регистрация словаря в БД.

        Args:
            session: сессия SQLAlchemy
            dictionary: словарь

        Returns:
            id словаря
        """
        name = dictionary.name()
        model = session.query(Dictionary).filter_by(name=name).first()

        if not model:
            model = Dictionary(name=name)
            session.add(model)
            session.flush()

        return model.id

    def _mark_term_as_known(self, session: Session, dictionary_id: int, term_id: int, result: TermDTO) -> None:
        """
        Записать термин как найденный в словаре.

        Args:
            session: сессия SQLAlchemy
            dictionary_id: id словаря
            term_id: id термина
            result: DTO найденного термина
        """
        ref = TermDictionaryRef(term_id=term_id, dictionary_id=dictionary_id)

        stmt = insert(TermDictionaryRef).values(
            term_id=ref.term_id,
            dictionary_id=ref.dictionary_id,
            ref_id=result.ref_id,
        ).on_conflict_do_nothing(index_elements=["term_id", "dictionary_id"])

        session.execute(stmt)
