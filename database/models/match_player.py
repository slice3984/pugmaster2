from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from . import Match, CommunityPlayer

class MatchPlayer(Base):
    """Represents a player in a match and their rating change."""

    __tablename__ = 'match_players'
    match_id: Mapped[int] = mapped_column(
        ForeignKey('matches.id', ondelete='CASCADE'),
        primary_key=True
    )

    community_player_id: Mapped[int] = mapped_column(
        ForeignKey('community_players.id', ondelete='CASCADE'),
        primary_key=True
    )

    team: Mapped[int | None]
    mu: Mapped[float | None]
    sigma: Mapped[float | None]

    match: Mapped[Match] = relationship(back_populates='players')
    community_player: Mapped[CommunityPlayer] = relationship(back_populates='match_records')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'match_id={self.match_id!r}, '
            f'team={self.team!r}, '
            f'mu={self.mu!r}, '
            f'sigma={self.sigma!r}'
            f')'
        )