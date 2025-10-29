import datetime
from unittest.mock import patch, MagicMock

from src.modules.fetcher.pubmed.pub_med_fetcher import PubMedFetcher
from src.orm.models import Article


class TestPubMedFetcher:

    @patch("src.modules.fetcher.pubmed.pub_med_fetcher.Medline")
    @patch("src.modules.fetcher.pubmed.pub_med_fetcher.Entrez")
    def test_handle(self, mock_entrez, mock_medline, db_session):
        """Проверка, что модуль получает статьи и сохраняет их в БД"""

        # Мок Entrez.read
        mock_entrez.read.return_value = {"IdList": ["12345"]}

        # Мок Medline
        mock_medline.parse.return_value = [
            {
                "PMID": "12345",
                "TI": "Test Title",
                "AB": "Test Abstract",
                "AU": ["Test Author"],
                "DP": "2025",
            }
        ]

        # Запуск модуля
        module = PubMedFetcher(term="test")
        module.handle()

        # Проверка, что Entrez вызывался корректно
        mock_entrez.esearch.assert_called_once_with(db="pmc", term="test", retmax=10000)
        mock_entrez.efetch.assert_called_once_with(db="pmc", id="12345", rettype="medline", retmode="text")

        # Проверяем, что статья записалась в БД
        saved_article = db_session.query(Article).filter_by(pmid="12345").first()
        assert isinstance(saved_article, Article)
        assert saved_article.title == "Test Title"
        assert saved_article.authors == "Test Author"
        assert saved_article.abstract == "Test Abstract"
        assert saved_article.pubdate == datetime.date(2025, 1, 1)
