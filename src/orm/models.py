import datetime

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column
from src.config.database import Base


class Articles(Base):
    __tablename__ = 'articles'

    id: Mapped[int] = mapped_column(primary_key=True)
    pmid: Mapped[str]
    author: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    abstract: Mapped[str] = mapped_column(Text)
    pubdate: Mapped[datetime.date]
