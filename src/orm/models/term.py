from typing import TYPE_CHECKING

from sqlalchemy import Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates

from src.orm.database import BaseModel

# Обход проблемы циклического импорта:
if TYPE_CHECKING:
    from src.orm.models import TermDictionaryRef, ArticleTermAnnotation, Dictionary


class Term(BaseModel):
    __tablename__ = "terms"

    id: Mapped[int] = mapped_column(primary_key=True)
    term_text: Mapped[str] = mapped_column(Text, nullable=False, comment="Выделенный термин", unique=True)
    word_count: Mapped[int] = mapped_column(nullable=False, comment="Количество слов в термине")
    pos_model: Mapped[str] = mapped_column(nullable=False, comment="Структурная модель термина (POS-теги)")

    # Связи с другими таблицами БД
    annotations: Mapped[list["ArticleTermAnnotation"]] = relationship("ArticleTermAnnotation", back_populates="term",
                                                                      cascade="all, delete-orphan")
    # Связь с ассоциативной таблицей
    term_dictionary_refs: Mapped[list["TermDictionaryRef"]] = relationship(
        "TermDictionaryRef",
        back_populates="term",
        cascade="all, delete-orphan"
    )
    # Простая many-to-many связь
    dictionaries: Mapped[list["Dictionary"]] = relationship(
        "Dictionary",
        secondary="term_dictionary_ref",
        back_populates="terms",
        overlaps="term_dictionary_refs"
    )

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
        pos_model = self.pos_model

        return f"{id=}\n{term_text=}\n{word_count=}\n{pos_model=}"
