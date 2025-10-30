from sqlalchemy import Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates

from src.orm.database import BaseModel
from src.orm.models import Article


class Term(BaseModel):
    __tablename__ = 'terms'

    id: Mapped[int] = mapped_column(primary_key=True)
    term_text: Mapped[str] = mapped_column(Text, nullable=False, comment="Выделенный термин")
    word_count: Mapped[int] = mapped_column(nullable=False, comment="Количество слов в термине")
    article_id: Mapped[int] = mapped_column(ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)
    start_char: Mapped[int] = mapped_column(nullable=False, comment="Позиция в abstract: начало")
    end_char: Mapped[int] = mapped_column(nullable=False, comment="Позиция в abstract: конец")

    # Relationship to Article
    article: Mapped["Article"] = relationship("Article", backref="terms")

    __table_args__ = (
        Index('idx_term_text', 'term_text'),
        Index('idx_article_id', 'article_id'),
    )

    @validates('term_text')
    def validate_term_text(self, key, value) -> str:
        if not value or len(value.strip()) == 0:
            raise ValueError("Term text cannot be empty")
        return value.strip().lower()

    @validates('word_count')
    def validate_word_count(self, key, value) -> int:
        if value < 1:
            raise ValueError("Word count must be at least 1")
        return value

    @validates('start_char', 'end_char')
    def validate_positions(self, key, value) -> int:
        if value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value

    def __str__(self):

        id = self.id
        term_text = self.term_text
        word_count = self.word_count
        article_id = self.article_id
        start_char = self.start_char
        end_char = self.end_char

        return f"{id=}\n{term_text=}\n{word_count=}\n{article_id=}\n{start_char=}\n{end_char=}"
