import datetime

from sqlalchemy import Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import validates

from src.orm.database import BaseModel


class Article(BaseModel):
    __tablename__ = 'articles'

    id: Mapped[int] = mapped_column(primary_key=True)
    pmcid: Mapped[str] = mapped_column(unique=True, index=True, nullable=True, comment="PMC")
    authors: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    pubdate: Mapped[datetime.date] = mapped_column(nullable=False)

    __table_args__ = (
        Index('idx_pubdate', 'pubdate'),
    )

    @validates('pmcid')
    def validate_pmcid(self, key, value) -> None:
        if not value or len(value.strip()) == 0:
            raise ValueError("PMC cannot be empty")
        if len(value) > 50:
            raise ValueError("PMC too long")
        return value.strip()

    @validates('abstract')
    def validate_abstract(self, key, value) -> None:
        if not value or len(value.strip()) == 0:
            raise ValueError("Abstract cannot be empty")
        return value
