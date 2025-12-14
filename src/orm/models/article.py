import datetime
from datetime import date, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import Text, Index, JSON
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
    pmid: Mapped[str] = mapped_column(unique=True, index=True, nullable=True, comment="Идентификатор PMID")
    title: Mapped[str] = mapped_column(Text, nullable=False, comment="Название статьи")
    authors: Mapped[str] = mapped_column(Text, nullable=False, comment="Список авторов")
    abstract: Mapped[str] = mapped_column(Text, nullable=False, comment="Аннотация")
    pubdate: Mapped[datetime.date] = mapped_column(nullable=False, comment="Дата публикации")
    author_keywords: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=True,
        comment="Авторские ключевые слова (поле OT)"
    )
    publication_type: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=True,
        comment="Тип публикации (поле PT)"
    )

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
            raise ValueError("Поле pmcid не может быть пустым")
        if len(value) > 50:
            raise ValueError("Поле pmcid слишком длинное")
        return value.strip()

    @validates("pmid")
    def validate_pmid(self, key, value) -> None:
        if not value or len(value.strip()) == 0:
            raise ValueError("Поле pmid не может быть пустым")
        if len(value) > 50:
            raise ValueError("Поле pmid слишком длинное")
        return value.strip()

    @validates("abstract")
    def validate_abstract(self, key, value) -> None:
        if not value or len(value.strip()) == 0:
            raise ValueError("Поле abstract не может быть пустым")
        return value

    @validates("pubdate")
    def validate_pubdate(self, key, value) -> None:
        tomorrow = date.today() + timedelta(days=1)
        if value >= tomorrow:
            raise ValueError("Поле pubdate не может быть в будущем")
        return value

    def get_text(self, field: str) -> str:
        return getattr(self, field)

    def __str__(self):

        identifier = (
            f"pmcid={self.pmcid}"
            if self.pmcid is not None
            else f"pmid={self.pmid}"
        )

        return (
            f"id={self.id}\n"
            f"{identifier}\n"
            f"title={self.title}\n"
            f"authors={self.authors}\n"
            f"abstract={self.abstract}\n"
            f"pubdate={self.pubdate}"
        )
