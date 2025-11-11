from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.orm.database import BaseModel

# Обход проблемы циклического импорта:
if TYPE_CHECKING:
    from src.orm.models import ArticleTermAnnotation


class Module(BaseModel):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, comment="Название модуля", unique=True)

    # Связи с другими таблицами БД
    annotations: Mapped[list["ArticleTermAnnotation"]] = relationship("ArticleTermAnnotation", back_populates="module",
                                                                      cascade="all, delete-orphan")

    __table_args__ = (
        {"comment": "Модули системы"}
    )

    def __str__(self):
        id = self.id
        name = self.name

        return f"{id=}\n{name=}"
