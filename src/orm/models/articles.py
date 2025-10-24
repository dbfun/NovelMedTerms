import datetime

from sqlalchemy import Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import validates

from src.orm.database import BaseModel


class Articles(BaseModel):
    __tablename__ = 'articles'

    id: Mapped[int] = mapped_column(primary_key=True)
    pmid: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    authors: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    pubdate: Mapped[datetime.date] = mapped_column(nullable=False)

    __table_args__ = (
        Index('idx_pubdate', 'pubdate'),
    )

    @validates('pmid')
    def validate_pmid(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("PMID cannot be empty")
        if len(value) > 20:
            raise ValueError("PMID too long")
        return value.strip()
