from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..column_types import CreatedAt
from . import Base

if TYPE_CHECKING:
    from . import CommunityPlayer, Community

class CommunityPlayerWarn(Base):
    """Represents a warning of a community player."""

    __tablename__ = 'community_player_warns'
    id: Mapped[int] = mapped_column(primary_key=True)
    community_id: Mapped[int] = mapped_column(
        ForeignKey('communities.id', ondelete='CASCADE'),
    )

    community_player_id: Mapped[int] = mapped_column(
        ForeignKey('community_players.id', ondelete='CASCADE')
    )

    issuer_community_player_id: Mapped[int | None] = mapped_column(
        ForeignKey('community_players.id', ondelete='CASCADE')
    )

    reason: Mapped[str | None] = mapped_column(String(255))
    warned_at: Mapped[CreatedAt]
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    community: Mapped[Community] = relationship(back_populates='warns')

    player: Mapped[CommunityPlayer] = relationship(
        back_populates='warns',
        foreign_keys=[community_player_id]
    )

    issuer: Mapped[CommunityPlayer] = relationship(
        back_populates='issued_warns',
        foreign_keys=[issuer_community_player_id]
    )

    __table_args__ = (
        CheckConstraint('length(reason) BETWEEN 1 and 255', name='reason_length'),
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'reason={self.reason!r}, '
            f'warned_at={self.warned_at!r}, '
            f'revoked_at={self.revoked_at!r}'
            f')'
        )