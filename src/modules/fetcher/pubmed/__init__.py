import datetime
import logging

from Bio import Entrez, Medline
from dateutil import parser
from sqlalchemy.dialects.postgresql import insert

from src.config.ncbi import NcbiConfig
from src.modules.module import Module, ModuleInfo
from src.orm.models import Article


class PubMedCentralFetcher(Module):
    """
    Модуль для получения статей из PubMed Central.

    Документация по параметрам
    https://www.ncbi.nlm.nih.gov/books/NBK25497/#chapter2.chapter2_table1

    Значения параметра "db"
    https://milliams.com/courses/biopython/Databases.html

    Значения параметров "retmode" и "rettype"
    https://www.ncbi.nlm.nih.gov/books/NBK25499/table/chapter4.T._valid_values_of__retmode_and/?report=objectonly
    """

    BATCH_SIZE: int = 100

    def __init__(self, term: str, retmax: int):
        """
        Args:
            term: строка поиска по PubMed Central
            retmax: лимит поиска
        """
        self.logger = logging.getLogger(PubMedCentralFetcher.info().name())
        self.term = term
        self.retmax = retmax
        Entrez.email = NcbiConfig.email()
        Entrez.api_key = NcbiConfig.api_key()

    @staticmethod
    def info() -> ModuleInfo:
        return ModuleInfo(module="fetcher", type="pubmed-central")

    def handle(self) -> None:
        """Запуск импорта статей"""
        from src.container import container

        with container.db_session() as session:

            # Поиск статей по термину
            with Entrez.esearch(db="pmc", term=self.term, retmax=self.retmax) as search_handle:
                record = Entrez.read(search_handle)
                id_list = record.get("IdList", [])

            self.logger.info(f"Найдено статей: {len(id_list)}")

            # Загрузка данных батчами
            # Если id="12528561", то PMC="PMC12528561" - по факту.

            for i in range(0, len(id_list), self.BATCH_SIZE):
                batch_ids = id_list[i:i + self.BATCH_SIZE]
                self.logger.debug(f"Пакетная загрузка: {i}-{min(i + self.BATCH_SIZE, len(id_list))} из {len(id_list)}")
                with Entrez.efetch(db="pmc", id=batch_ids, rettype="medline", retmode="text") as fetch_handle:
                    records = Medline.parse(fetch_handle)
                    for rec in records:
                        try:
                            article = Article(
                                pmcid=rec.get("PMC"),
                                title=rec.get("TI"),
                                abstract=rec.get("AB"),
                                authors=", ".join(rec.get("AU", [])),
                                pubdate=self._parse_pubdate(rec.get("DP")),
                            )

                            stmt = insert(Article).values(
                                pmcid=article.pmcid,
                                title=article.title,
                                abstract=article.abstract,
                                authors=article.authors,
                                pubdate=article.pubdate
                            ).on_conflict_do_nothing(index_elements=["pmcid"])

                            session.execute(stmt)

                        except ValueError as e:
                            self.logger.warning(f"Пропускаем запись: {rec.get("PMC")} - {e}")
                            continue

                session.commit()

    @staticmethod
    def _parse_pubdate(dp_value: str | None) -> datetime.date | None:
        """Парсит поле DP (Date of Publication) в datetime.date."""
        if not dp_value:
            return None

        try:
            # Пробуем парсить с помощью dateutil (умный разбор)
            dt = parser.parse(dp_value, fuzzy=True, default=datetime.datetime(1900, 1, 1))
            return datetime.date(dt.year, dt.month, dt.day)
        except Exception:
            # В случае ошибки пробуем получить хотя бы год
            parts = dp_value.split()
            if parts and parts[0].isdigit():
                return datetime.date(int(parts[0]), 1, 1)
            return None
