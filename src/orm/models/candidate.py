from typing import TYPE_CHECKING, Dict

from sqlalchemy import ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.orm.database import BaseModel

# Обход проблемы циклического импорта:
if TYPE_CHECKING:
    from src.orm.models import Term


class Candidate(BaseModel):
    __tablename__ = 'candidates'

    id: Mapped[int] = mapped_column(primary_key=True)
    term_id: Mapped[int] = mapped_column(ForeignKey('terms.id', ondelete='CASCADE'), nullable=False, unique=True,
                                         comment='Термин')

    first_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Год первого упоминания'
    )
    
    last_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Год последнего упоминания'
    )

    first_stable_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Год появления минимальной устойчивости'
    )
    
    max_consecutive: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Максимальное число лет подряд с ненулевой частотой'
    )
    
    growth: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment='Коэффициент роста частоты (max / first)'
    )
    
    total_mentions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Общее число упоминаний термина'
    )
    
    counts_per_year: Mapped[Dict[int, int]] = mapped_column(
        JSON,
        nullable=False,
        comment='Частота термина по годам'
    )

    # Связи с другими таблицами БД
    term: Mapped['Term'] = relationship(
        'Term',
        back_populates='candidates'
    )