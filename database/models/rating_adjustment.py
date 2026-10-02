from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from ..column_types import CreatedAt

if TYPE_CHECKING:
    from . import Queue, Season, CommunityPlayer

class RatingAdjustment(Base):
    """Represents a rating adjustment for a given player for a specific queue in a season."""

    __tablename__ = 'rating_adjustments'
    id: Mapped[int] = mapped_column(primary_key=True)
    queue_id: Mapped[int] = mapped_column(ForeignKey('queues.id', ondelete='CASCADE'))
    season_id: Mapped[int] = mapped_column(ForeignKey('seasons.id', ondelete='CASCADE'))
    community_player_id: Mapped[int] = mapped_column(ForeignKey('community_players.id', ondelete='CASCADE'))
    after_match_id: Mapped[int | None] = mapped_column(ForeignKey('matches.id', ondelete='CASCADE'))
    mu: Mapped[float]
    sigma: Mapped[float]
    created_at: Mapped[CreatedAt]

    season: Mapped[Season] = relationship(back_populates='rating_adjustments')
    queue: Mapped[Queue] = relationship()
    community_player: Mapped[CommunityPlayer] = relationship(back_populates='rating_adjustments')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'mu={self.mu!r}, '
            f'sigma={self.sigma!r}, '
            f'created_at={self.created_at!r}'
            f')'
        )