from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column

from . import Base
from ..column_types import CreatedAt

class BotSettings(Base):
    """General bot settings for the bot instance, stores heartbeat state too."""

    __tablename__ = 'bot_settings'
    id: Mapped[int] = mapped_column(primary_key=True)
    last_heartbeat_at: Mapped[CreatedAt]

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'last_heartbeat_at={self.last_heartbeat_at!r}'
            f')'
        )