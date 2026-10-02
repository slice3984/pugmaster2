from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, false, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from ..column_types import CreatedAt

if TYPE_CHECKING:
    from . import Season, Queue, MatchPlayer

class Match(Base):
    """Represents a played match in a season."""

    __tablename__ = 'matches'
    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(
        ForeignKey('seasons.id', ondelete='CASCADE'),
    )
    queue_id: Mapped[int] = mapped_column(
        ForeignKey('queues.id', ondelete='CASCADE'),
    )
    map: Mapped[str | None]
    is_rated: Mapped[bool] = mapped_column(server_default=false())
    rated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    winning_team: Mapped[int | None]
    created_at: Mapped[CreatedAt]

    season: Mapped[Season] = relationship(back_populates='matches')
    queue: Mapped[Queue] = relationship(back_populates='matches')
    players: Mapped[list[MatchPlayer]] = relationship(
        back_populates='match',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'map={self.map!r}, '
            f'is_rated={self.is_rated!r}, '
            f'rated_at={self.rated_at!r}, '
            f'winning_team={self.winning_team!r}, '
            f'created_at={self.created_at!r}'
            f')'
        )