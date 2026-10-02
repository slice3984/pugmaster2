from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from ..column_types import CreatedAt

if TYPE_CHECKING:
    from . import (Messenger, CommunityPlayer, CommunitySettings, MapPool, Queue,
                   CommunityCommandSettings, CommunityPlayerWarn, CommunityPlayerBan,
                   ServerPool, Season)


class Community(Base):
    """Represents a community merging multiple platforms."""

    __tablename__ = 'communities'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[CreatedAt]

    messengers: Mapped[list[Messenger]] = relationship(
        back_populates='community',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    players: Mapped[list[CommunityPlayer]] = relationship(
        back_populates='community',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    settings: Mapped[CommunitySettings] = relationship(
        back_populates='community',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    map_pools: Mapped[list[MapPool]] = relationship(
        back_populates='community',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    queues: Mapped[list[Queue]] = relationship(
        back_populates='community',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    command_settings: Mapped[list[CommunityCommandSettings]] = relationship(
        back_populates='community',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    warns: Mapped[list[CommunityPlayerWarn]] = relationship(
        back_populates='community',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    bans: Mapped[list[CommunityPlayerBan]] = relationship(
        back_populates='community',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    servers: Mapped[list[ServerPool]] = relationship(
        back_populates='community',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    seasons: Mapped[list[Season]] = relationship(
        back_populates='community',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'created_at={self.created_at!r})'
        )
