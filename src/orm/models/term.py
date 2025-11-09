from typing import TYPE_CHECKING

from sqlalchemy import Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates

from src.orm.database import BaseModel

# Обход проблемы циклического импорта:
# ImportError: cannot import name 'ArticleTermAnnotations' from partially initialized module 'src.orm.models' (most likely due to a circular import)
# SQLAlchemy использует строки (Mapped["Term"]), а этот импорт нужен для подсветки в IDE.
if TYPE_CHECKING:
    from src.orm.models import ArticleTermAnnotation, Dictionary


class Term(BaseModel):
    __tablename__ = "terms"

    id: Mapped[int] = mapped_column(primary_key=True)
    term_text: Mapped[str] = mapped_column(Text, nullable=False, comment="Выделенный термин", unique=True)
    word_count: Mapped[int] = mapped_column(nullable=False, comment="Количество слов в термине")

    # Связи с другими таблицами БД
    annotations: Mapped[list["ArticleTermAnnotation"]] = relationship("ArticleTermAnnotation", back_populates="term",
                                                                      cascade="all, delete-orphan")
    dictionaries: Mapped[list["Dictionary"]] = relationship("Dictionary", secondary="term_dictionary_ref",
                                                            back_populates="terms")

    __table_args__ = (
        Index("idx_term_text", "term_text"),
        {"comment": "Извлеченные термины"}
    )

    @validates("term_text")
    def validate_term_text(self, key, value) -> str:
        if not value or len(value.strip()) == 0:
            raise ValueError("term_text должен быть заполнен")
        return value.strip().lower()

    @validates("word_count")
    def validate_word_count(self, key, value) -> int:
        if value < 1:
            raise ValueError("word_count должен быть >= 1")
        return value

    def __str__(self):

        id = self.id
        term_text = self.term_text
        word_count = self.word_count

        return f"{id=}\n{term_text=}\n{word_count=}"
