import datetime
from unittest.mock import patch, MagicMock

from src.modules.fetcher.pubmed import PubMedCentralFetcher
from src.orm.models import Article


class TestPubMedFetcher:

    @patch("src.modules.fetcher.pubmed.Medline")
    @patch("src.modules.fetcher.pubmed.Entrez")
    def test_handle(self, mock_entrez, mock_medline, db_session):
        """Проверка, что модуль получает статьи и сохраняет их в БД"""

        # Мок Entrez.read
        mock_entrez.read.return_value = {"IdList": ["12345"]}

        # Мок Medline
        mock_medline.parse.return_value = [
            {
                "PMC": "PMC12345",
                "TI": "Test Title",
                "AB": "Test Abstract",
                "AU": ["Test Author"],
                "DP": "2025",
            }
        ]

        retmax=100
        term="term"

        # Запуск модуля
        module = PubMedCentralFetcher(term=term, retmax=retmax)
        module.handle()

        # Проверка, что Entrez вызывался корректно
        mock_entrez.esearch.assert_called_once_with(db="pmc", term=term, retmax=retmax)
        mock_entrez.efetch.assert_called_once_with(db="pmc", id=["12345"], rettype="medline", retmode="text")

        # Проверяем, что статья записалась в БД
        saved_article = db_session.query(Article).filter_by(pmcid="PMC12345").first()
        assert isinstance(saved_article, Article)
        assert saved_article.title == "Test Title"
        assert saved_article.authors == "Test Author"
        assert saved_article.abstract == "Test Abstract"
        assert saved_article.pubdate == datetime.date(2025, 1, 1)
