from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, true, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from . import BotCommand, Community, CommunityCommandOverride

class CommunityCommandSettings(Base):
    """Community specific bot command settings."""

    __tablename__ = 'community_command_settings'
    id: Mapped[int] = mapped_column(primary_key=True)

    community_id: Mapped[int] = mapped_column(
        ForeignKey('communities.id', ondelete='CASCADE'),
    )

    command_id: Mapped[int] = mapped_column(ForeignKey('bot_commands.id', ondelete='CASCADE'))
    is_enabled: Mapped[bool] = mapped_column(server_default=true())

    command: Mapped[BotCommand] = relationship(back_populates='community_settings')
    community: Mapped[Community] = relationship(back_populates='command_settings')

    overrides: Mapped[list[CommunityCommandOverride]] = relationship(
        back_populates='command_settings',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint('community_id', 'command_id'),
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'is_enabled={self.is_enabled!r}'
            f')'
        )