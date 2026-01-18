import logging

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from src.orm.models import Article

old_level = None


def disable_logging() -> None:
    """
    Временное отключение журналирования.
    Полезно при вызове библиотек (matplotlib.pyplot), которые избыточно журналируют.
    """
    global old_level
    logger = logging.getLogger()
    old_level = logger.level
    logger.setLevel(logging.CRITICAL)


def enable_logging() -> None:
    """
    Возврат журналирования к прошлому состоянию
    """
    global old_level
    logger = logging.getLogger()
    logger.setLevel(old_level)

def all_years_range(session: Session) -> range:
    """
    Returns:
        Интервал годов по всем статьям, например range(2005, 2025).
    """
    result = session.query(
        func.min(extract('year', Article.pubdate)).label('min_year'),
        func.max(extract('year', Article.pubdate)).label('max_year')
    ).one()

    min_year = int(result.min_year)
    max_year = int(result.max_year)

    return range(min_year, max_year + 1)