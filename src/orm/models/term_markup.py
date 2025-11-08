from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates

from src.orm.database import BaseModel

# Обход проблемы циклического импорта:
# ImportError: cannot import name 'TermMarkup' from partially initialized module 'src.orm.models' (most likely due to a circular import)
# SQLAlchemy использует строки (Mapped["Term"]), а этот импорт нужен для подсветки в IDE.
if TYPE_CHECKING:
    from src.orm.models import Article
    from src.orm.models.term import Term


class TermMarkup(BaseModel):
    __tablename__ = 'term_markups'

    id: Mapped[int] = mapped_column(primary_key=True)
    term_id: Mapped[int] = mapped_column(ForeignKey('terms.id', ondelete='CASCADE'), nullable=False)
    article_id: Mapped[int] = mapped_column(ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)
    module_name: Mapped[str] = mapped_column(nullable=False, comment="Модуль, который извлек термин")
    start_char: Mapped[int] = mapped_column(nullable=False, comment="Позиция в abstract: начало")
    end_char: Mapped[int] = mapped_column(nullable=False, comment="Позиция в abstract: конец")

    # Связи с другими таблицами БД
    term: Mapped["Term"] = relationship("Term", back_populates="markups")
    article: Mapped["Article"] = relationship("Article", back_populates="markups")

    __table_args__ = (
        Index('idx_term_id', 'term_id'),
        Index('idx_article_id', 'article_id'),
    )

    @validates('start_char', 'end_char')
    def validate_positions(self, key, value) -> int:
        if value < 0:
            raise ValueError(f"{key} не может быть отрицательным")
        return value

    def __str__(self):
        id = self.id
        term_id = self.term_id
        article_id = self.article_id
        module_name = self.module_name
        start_char = self.start_char
        end_char = self.end_char

        return f"{id=}\n{term_id=}\n{article_id=}\n{module_name=}\n{start_char=}\n{end_char=}"
