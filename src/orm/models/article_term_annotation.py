from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates

from src.orm.database import BaseModel

# Обход проблемы циклического импорта:
# ImportError: cannot import name 'ArticleTermAnnotations' from partially initialized module 'src.orm.models' (most likely due to a circular import)
# SQLAlchemy использует строки (Mapped["Term"]), а этот импорт нужен для подсветки в IDE.
if TYPE_CHECKING:
    from src.orm.models import Article, Term, Module


class ArticleTermAnnotation(BaseModel):
    __tablename__ = "article_term_annotations"

    id: Mapped[int] = mapped_column(primary_key=True)
    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id", ondelete="CASCADE"), nullable=False,
                                         comment="Термин")
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), nullable=False,
                                            comment="Статья")
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id", ondelete="CASCADE"), nullable=False,
                                           comment="Модуль, который извлек термин")
    start_char: Mapped[int] = mapped_column(nullable=False, comment="Позиция в abstract: начало")
    end_char: Mapped[int] = mapped_column(nullable=False, comment="Позиция в abstract: конец")

    # Связи с другими таблицами БД
    term: Mapped["Term"] = relationship("Term", back_populates="annotations")
    article: Mapped["Article"] = relationship("Article", back_populates="annotations")
    module: Mapped["Module"] = relationship("Module", back_populates="annotations")

    __table_args__ = (
        Index("idx_term_id", "term_id"),
        Index("idx_article_id", "article_id"),
        Index("idx_module_id", "module_id"),
        {"comment": "Разметка статей по терминам"}
    )

    @validates("start_char", "end_char")
    def validate_positions(self, key, value) -> int:
        if value < 0:
            raise ValueError(f"{key} не может быть отрицательным")
        return value

    def __str__(self):
        id = self.id
        term_id = self.term_id
        article_id = self.article_id
        module_id = self.module_id
        start_char = self.start_char
        end_char = self.end_char

        return f"{id=}\n{term_id=}\n{article_id=}\n{module_id=}\n{start_char=}\n{end_char=}"
