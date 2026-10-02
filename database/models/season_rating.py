from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from . import Season, Queue, CommunityPlayer

class SeasonRating(Base):
    """Stores a player's rating for a specific queue and season."""

    __tablename__ = 'season_ratings'
    season_id: Mapped[int] = mapped_column(
        ForeignKey('seasons.id', ondelete='CASCADE'),
        primary_key=True
    )

    queue_id: Mapped[int] = mapped_column(
        ForeignKey('queues.id', ondelete='CASCADE'),
        primary_key=True
    )

    community_player_id: Mapped[int] = mapped_column(
        ForeignKey('community_players.id', ondelete='CASCADE'),
        primary_key=True
    )

    mu: Mapped[float]
    sigma: Mapped[float]

    season: Mapped[Season] = relationship(back_populates='season_ratings')
    queue: Mapped[Queue] = relationship(back_populates='season_ratings')
    community_player: Mapped[CommunityPlayer] = relationship(back_populates='season_ratings')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'season_id={self.season_id!r}, '
            f'queue_id={self.queue_id!r}, '
            f'mu={self.mu!r}, '
            f'sigma={self.sigma!r}'
            f')'
        )