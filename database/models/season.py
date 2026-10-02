from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from ..column_types import CreatedAt

if TYPE_CHECKING:
    from . import Community, SeasonRating, Match, RatingAdjustment

class Season(Base):
    """Represents a season that groups matches and player ratings."""

    __tablename__ = 'seasons'
    id: Mapped[int] = mapped_column(primary_key=True)
    community_id: Mapped[int] = mapped_column(
        ForeignKey('communities.id', ondelete='CASCADE'),
    )
    name: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[CreatedAt]
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    community: Mapped[Community] = relationship(back_populates='seasons')

    season_ratings: Mapped[list[SeasonRating]] = relationship(
        back_populates='season',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    matches: Mapped[list[Match]] = relationship(
        back_populates='season',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    rating_adjustments: Mapped[list[RatingAdjustment]] = relationship(
        back_populates='season',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint('community_id', 'name'),
        CheckConstraint('length(name) BETWEEN 1 AND 32', name='name_length'),
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'created_at={self.created_at!r}, '
            f'ended_at={self.ended_at!r}'
            f')'
        )