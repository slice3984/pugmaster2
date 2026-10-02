from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from ..column_types import CreatedAt

if TYPE_CHECKING:
    from . import Queue, CommunityPlayer

class QueueEntry(Base):
    """Represents a queue entry for a queue, used for state recovery."""

    __tablename__ = 'queue_entries'
    queue_id: Mapped[int] = mapped_column(
        ForeignKey('queues.id', ondelete='CASCADE'),
        primary_key=True,
    )

    community_player_id: Mapped[int] = mapped_column(
        ForeignKey('community_players.id', ondelete='CASCADE'),
        primary_key=True,
    )

    joined_at: Mapped[CreatedAt]

    queue: Mapped[Queue] = relationship(back_populates='entries')
    community_player: Mapped[CommunityPlayer] = relationship(back_populates='queue_entries')

    __table_args__ = (
        UniqueConstraint('queue_id', 'community_player_id'),
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'queue_id={self.queue_id!r}, '
            f'community_player_id={self.community_player_id!r}, '
            f'joined_at={self.joined_at!r}'
            f')'
        )