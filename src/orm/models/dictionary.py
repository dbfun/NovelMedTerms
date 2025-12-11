from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.orm.database import BaseModel

# Обход проблемы циклического импорта:
if TYPE_CHECKING:
    from src.orm.models import Term, TermDictionaryRef


class Dictionary(BaseModel):
    __tablename__ = "dictionaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, comment="Название словаря", unique=True)

    # Связи с другими таблицами БД
    # Связь с ассоциативной таблицей
    term_dictionary_refs: Mapped[list["TermDictionaryRef"]] = relationship(
        "TermDictionaryRef",
        back_populates="dictionary",
        cascade="all, delete-orphan"
    )
    # Простая many-to-many связь
    terms: Mapped[list["Term"]] = relationship(
        "Term",
        secondary="term_dictionary_ref",
        back_populates="dictionaries",
        overlaps="term_dictionary_refs"
    )

    __table_args__ = (
        {"comment": "Словари терминов"}
    )

    @staticmethod
    def filter_not_in_dict(dictionaries: list) -> tuple:
        """
        Метод-помощник для фильтрации терминов, которые есть в словарях терминов.

        Args:
            dictionaries: список словарей
        Returns:
            Части SQL-выражения и параметры.
        """
        join_tables = []
        where_cond = []
        params = {}

        # Проходим по списку словарей и подготавливаем части SQL для постановки в финальный запрос.
        for idx, dictionary in enumerate(dictionaries):
            # Для множественного объединения таблиц используем алиасы.
            table_alias = f"ref_{idx}"

            # Параметр для dictionary_id
            param_name = f"dict_id_{idx}"
            params[param_name] = dictionary.id

            join_tables.append(
                f"""
                LEFT JOIN term_dictionary_ref {table_alias}
                       ON {table_alias}.term_id = t.id
                      AND {table_alias}.dictionary_id = :{param_name}"""
            )
            where_cond.append(f"""
                AND {table_alias}.id IS NULL""")

        joins_sql = "\n".join(join_tables)
        where_sql = "\n".join(where_cond)

        return params, joins_sql, where_sql

    def __str__(self):
        id = self.id
        name = self.name

        return f"{id=}\n{name=}"
