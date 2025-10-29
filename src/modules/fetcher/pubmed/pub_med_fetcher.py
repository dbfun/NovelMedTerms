import datetime

from Bio import Entrez, Medline
from dateutil import parser

from src.config.ncbi import NcbiConfig
from src.modules.module import Module
from src.modules.module_registry import register_module
from src.orm.models import Article


@register_module(module="fetcher", type="pubmed")
class PubMedFetcher(Module):
    """
    Модуль для получения статей из PubMed.

    Документация по параметрам
    https://www.ncbi.nlm.nih.gov/books/NBK25497/#chapter2.chapter2_table1

    Значения параметра "db"
    https://milliams.com/courses/biopython/Databases.html

    Значения параметров "retmode" и "rettype"
    https://www.ncbi.nlm.nih.gov/books/NBK25499/table/chapter4.T._valid_values_of__retmode_and/?report=objectonly
    """

    def __init__(self, term: str):
        self.term = term
        Entrez.email = NcbiConfig.email()
        Entrez.api_key = NcbiConfig.api_key()

    def handle(self) -> None:
        from src.container import container
        session = container.db_session()

        # Поиск статей по термину

        with Entrez.esearch(db="pmc", term=self.term, retmax=10000) as search_handle:
            record = Entrez.read(search_handle)
            pmids = record.get("IdList", [])

        # Загрузка данных по каждому PMID
        for pmid in pmids:
            with Entrez.efetch(db="pmc", id=pmid, rettype="medline", retmode="text") as fetch_handle:
                records = Medline.parse(fetch_handle)
                for rec in records:
                    article = Article(
                        pmid=rec.get("PMID"),
                        title=rec.get("TI"),
                        abstract=rec.get("AB"),
                        authors=", ".join(rec.get("AU", [])),
                        pubdate=self._parse_pubdate(rec.get("DP"))
                    )
                    session.add(article)

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
            # fallback — только год
            parts = dp_value.split()
            if parts and parts[0].isdigit():
                return datetime.date(int(parts[0]), 1, 1)
            return None
