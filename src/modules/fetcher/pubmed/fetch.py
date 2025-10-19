from src.orm.models import Articles
from datetime import datetime


def fetch_from_pubmed(term: str):
    """Заглушка. В тестах будет заменена через mock."""
    raise NotImplementedError("Not implemented yet")


def import_pubmed(term: str, session):
    """
    Импортирует статьи по term в БД.
    Возвращает количество добавленных статей.
    """

    # Получаем статьи из PubMed (в тесте будет мок)
    articles_data = fetch_from_pubmed(term)

    count = 0
    for art in articles_data:
        # Преобразуем дату в datetime.date
        pubdate = datetime.strptime(art["pubdate"], "%Y-%m-%d").date()
        article = Articles(
            pmid=art["pmid"],
            title=art["title"],
            abstract=art["abstract"],
            author=art["author"],
            pubdate=pubdate,
        )
        session.add(article)
        count += 1

    session.commit()
    return count
