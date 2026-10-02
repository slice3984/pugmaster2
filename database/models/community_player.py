from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from ..column_types import CreatedAt

if TYPE_CHECKING:
    from . import (Community, MessengerPlayer, QueueEntry, CommunityPlayerWarn,
                   CommunityPlayerBan, SeasonRating, MatchPlayer, RatingAdjustment)

class CommunityPlayer(Base):
    """Represents a merged community player from different platforms."""

    __tablename__ = 'community_players'
    id: Mapped[int] = mapped_column(primary_key=True)
    community_id: Mapped[int] = mapped_column(ForeignKey('communities.id', ondelete='CASCADE'))
    joined_at: Mapped[CreatedAt]
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    allow_offline_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    community: Mapped[Community] = relationship(back_populates='players')

    messenger_players: Mapped[list[MessengerPlayer]] = relationship(
        back_populates='community_player',
        cascade='all',
        passive_deletes=True,
    )

    queue_entries: Mapped[list[QueueEntry]] = relationship(
        back_populates='community_player',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    warns: Mapped[list[CommunityPlayerWarn]] = relationship(
        back_populates='player',
        foreign_keys='CommunityPlayerWarn.community_player_id',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    issued_warns: Mapped[list[CommunityPlayerWarn]] = relationship(
        back_populates='issuer',
        foreign_keys='CommunityPlayerWarn.issuer_community_player_id',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    bans: Mapped[list[CommunityPlayerBan]] = relationship(
        back_populates='player',
        foreign_keys='CommunityPlayerBan.community_player_id',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    issued_bans: Mapped[list[CommunityPlayerBan]] = relationship(
        back_populates='issuer',
        foreign_keys='CommunityPlayerBan.issuer_community_player_id',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    season_ratings: Mapped[list[SeasonRating]] = relationship(
        back_populates='community_player',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    match_records: Mapped[list[MatchPlayer]] = relationship(
        back_populates='community_player',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    rating_adjustments: Mapped[list[RatingAdjustment]] = relationship(
        back_populates='community_player',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'joined_at={self.joined_at!r}, '
            f'expires_at={self.expires_at!r}, '
            f'allow_offline_expires_at={self.allow_offline_expires_at!r} '
            f')'
        )