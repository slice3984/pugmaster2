from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

from . import Base
from ..column_types import CreatedAt

if TYPE_CHECKING:
    from . import CommunityPlayer, Community

class CommunityPlayerBan(Base):
    """Represents a queue join ban of a community player."""

    __tablename__ = 'community_player_bans'
    id: Mapped[int] = mapped_column(primary_key=True)
    community_id: Mapped[int] = mapped_column(
        ForeignKey('communities.id', ondelete='CASCADE'),
    )

    community_player_id: Mapped[int] = mapped_column(
        ForeignKey('community_players.id', ondelete='CASCADE')
    )

    issuer_community_player_id: Mapped[int | None] = mapped_column(
        ForeignKey('community_players.id', ondelete='CASCADE'),
    )

    reason: Mapped[str | None] = mapped_column(String(255))
    banned_at: Mapped[CreatedAt]
    expiration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    community: Mapped[Community] = relationship(back_populates='bans')

    player: Mapped[CommunityPlayer] = relationship(
        back_populates='bans',
        foreign_keys=[community_player_id]
    )

    issuer: Mapped[CommunityPlayer | None] = relationship(
        back_populates='issued_bans',
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
            f'banned_at={self.banned_at!r}, '
            f'expiration_date={self.expiration_date!r}, '
            f'revoked_at={self.revoked_at!r}'
            f')'
        )
