from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.orm.database import BaseModel

# Обход проблемы циклического импорта:
if TYPE_CHECKING:
    from src.orm.models import Term, Dictionary


class TermDictionaryRef(BaseModel):
    __tablename__ = "term_dictionary_ref"

    id: Mapped[int] = mapped_column(primary_key=True)
    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id", ondelete="CASCADE"), nullable=False,
                                         comment="Термин")
    dictionary_id: Mapped[int] = mapped_column(ForeignKey("dictionaries.id", ondelete="CASCADE"), nullable=False,
                                               comment="Словарь")
    ref_id: Mapped[str] = mapped_column(Text, nullable=True, comment="Идентификатор термина в словаре (например, CUI)")

    # Связи с другими таблицами БД
    term: Mapped["Term"] = relationship(
        "Term",
        back_populates="term_dictionary_refs",
        overlaps="dictionaries,terms"
    )

    dictionary: Mapped["Dictionary"] = relationship(
        "Dictionary",
        back_populates="term_dictionary_refs",
        overlaps="dictionaries,terms"
    )

    __table_args__ = (
        UniqueConstraint("term_id", "dictionary_id"),
        {"comment": "Связь термина со словарем"}
    )

    def __str__(self):
        id = self.id
        term_id = self.term_id
        dictionary_id = self.dictionary_id

        return f"{id=}\n{term_id=}\n{dictionary_id=}"
