from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from . import CommunityCommandSettings

class BotCommand(Base):
    """Stores the name of a bot command."""

    __tablename__ = 'bot_commands'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    community_settings: Mapped[list[CommunityCommandSettings]] = relationship(
        back_populates='command',
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}'
            f')'
        )