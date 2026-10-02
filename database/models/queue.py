from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, true, String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums import PickModeType
from . import Base
from ..column_types import CreatedAt

if TYPE_CHECKING:
    from . import MapPool, Community, QueueEntry, SeasonRating, Match

class Queue(Base):
    """Contains the configuration of a Queue which belongs to a Community."""

    __tablename__ = 'queues'
    id: Mapped[int] = mapped_column(primary_key=True)
    community_id: Mapped[int] = mapped_column(ForeignKey('communities.id', ondelete='CASCADE'))
    map_pool_id: Mapped[int | None] = mapped_column(ForeignKey('map_pools.id', ondelete='SET NULL'))
    name: Mapped[str] = mapped_column(String(20))
    is_enabled: Mapped[bool] = mapped_column(server_default=true())
    default_queue: Mapped[bool] = mapped_column(server_default=false())
    player_count: Mapped[int]
    pick_mode: Mapped[PickModeType] = mapped_column(server_default=PickModeType.NO_TEAMS.value)
    afk_check: Mapped[bool] = mapped_column(server_default=true())
    promotion_role_uid: Mapped[str | None]
    created_at: Mapped[CreatedAt]

    community: Mapped[Community] = relationship(back_populates='queues')

    map_pool: Mapped[MapPool | None] = relationship(back_populates='queues')

    entries: Mapped[list[QueueEntry]] = relationship(
        back_populates='queue',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    season_ratings: Mapped[list[SeasonRating]] = relationship(
        back_populates='queue',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    matches: Mapped[list[Match]] = relationship(
        back_populates='queue',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    
    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'is_enabled={self.is_enabled!r}, '
            f'default_queue={self.default_queue!r}, '
            f'player_count={self.player_count!r}, '
            f'pick_mode={self.pick_mode.value!r}, '
            f'afk_check={self.afk_check!r}, '
            f'created_at={self.created_at!r}'
            f')'
        )