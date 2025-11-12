import logging
from sqlite3 import OperationalError
from typing import Optional

import owlready2
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm.session import Session

from src.modules.dictionary import TermDTO, Umls
from src.modules.module import Module, ModuleInfo
from src.orm.models import Term, TermDictionaryRef, Dictionary


class MeSH(Umls):
    """
    Вспомогательный класс для работы с MeSH.
    """

    def name(self) -> str:
        return 'MeSH (Medical Subject Headings) thesaurus'

    def dict(self) -> owlready2.pymedtermino2.model.MetaConcept:
        return self.onto["MSH"]

    def search(self, term: str) -> Optional[TermDTO]:
        for concept in self.dict().search(term):
            # Проверка на точное совпадение - не нужна, так как
            # "Heart Attack" возвращает "Myocardial Infarction",
            # что значит, что термин известен системе. Возвращаем первое совпадение.
            # Старый вариант: if concept.label[0].lower() == term.lower(): return TermDTO(ref_id=concept.name)
            return TermDTO(ref_id=concept.name)

        return None


class DictionaryMesh(Module):
    """
    Модуль поиска термина в словаре MeSH.

    Информация о MeSH
    -----------------


    MeSH (Medical Subject Headings) is the NLM controlled vocabulary thesaurus used for indexing articles for PubMed.

    Поиск: https://www.ncbi.nlm.nih.gov/mesh?cmd=search
    """

    def __init__(self):
        self.logger = logging.getLogger(DictionaryMesh.info().name())

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="dictionary", type="mesh")

    def handle(self) -> None:
        """Запуск поиска"""
        from src.container import container

        known_cnt = 0
        unknown_cnt = 0

        with container.db_session() as session:
            dictionary = MeSH()

            dictionary_id = self._register_dictionary_in_db(session, dictionary)

            # Получаем все статьи из БД
            terms = session.query(Term).all()

            for term in terms:
                try:
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

    def _register_dictionary_in_db(self, session: Session, dictionary: MeSH) -> int:
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
