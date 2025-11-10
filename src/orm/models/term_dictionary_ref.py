from sqlalchemy import ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.orm.database import BaseModel


class TermDictionaryRef(BaseModel):
    __tablename__ = "term_dictionary_ref"

    id: Mapped[int] = mapped_column(primary_key=True)
    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id", ondelete="CASCADE"), nullable=False,
                                         comment="Термин")
    dictionary_id: Mapped[int] = mapped_column(ForeignKey("dictionaries.id", ondelete="CASCADE"), nullable=False,
                                               comment="Словарь")
    ref_id: Mapped[str] = mapped_column(Text, nullable=True, comment="Идентификатор термина в словаре (например, CUI)")

    __table_args__ = (
        UniqueConstraint("term_id", "dictionary_id"),
        {"comment": "Связь термина со словарем"}
    )

    def __str__(self):
        id = self.id
        term_id = self.term_id
        dictionary_id = self.dictionary_id

        return f"{id=}\n{term_id=}\n{dictionary_id=}"
