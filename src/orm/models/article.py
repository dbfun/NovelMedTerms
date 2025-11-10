import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates

from src.orm.database import BaseModel

# Обход проблемы циклического импорта:
# ImportError: cannot import name 'ArticleTermAnnotations' from partially initialized module 'src.orm.models' (most likely due to a circular import)
# SQLAlchemy использует строки (Mapped["Term"]), а этот импорт нужен для подсветки в IDE.
if TYPE_CHECKING:
    from src.orm.models import ArticleTermAnnotation


class Article(BaseModel):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    pmcid: Mapped[str] = mapped_column(unique=True, index=True, nullable=True, comment="Идентификатор PMCID")
    title: Mapped[str] = mapped_column(Text, nullable=False, comment="Название статьи")
    authors: Mapped[str] = mapped_column(Text, nullable=False, comment="Список авторов")
    abstract: Mapped[str] = mapped_column(Text, nullable=False, comment="Аннотация")
    pubdate: Mapped[datetime.date] = mapped_column(nullable=False, comment="Дата публикации")

    # Связи с другими таблицами БД
    annotations: Mapped[list["ArticleTermAnnotation"]] = relationship("ArticleTermAnnotation", back_populates="article",
                                                                      cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_pubdate", "pubdate"),
        {"comment": "Научные статьи"}
    )

    @validates("pmcid")
    def validate_pmcid(self, key, value) -> None:
        if not value or len(value.strip()) == 0:
            raise ValueError("PMC cannot be empty")
        if len(value) > 50:
            raise ValueError("PMC too long")
        return value.strip()

    @validates("abstract")
    def validate_abstract(self, key, value) -> None:
        if not value or len(value.strip()) == 0:
            raise ValueError("Abstract cannot be empty")
        return value

    def __str__(self):

        id = self.id
        pmcid = self.pmcid
        title = self.title
        authors = self.authors
        abstract = self.abstract
        pubdate = self.pubdate

        return f"{id=}\n{pmcid=}\n{title=}\n{authors=}\n{abstract=}\n{pubdate=}"
