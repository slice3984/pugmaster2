from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from ..column_types import CreatedAt

if TYPE_CHECKING:
    from . import MessengerPlayer

class MessengerPlayerName(Base):
    """Represents a name the user is using currently or has used in the past."""

    __tablename__ = 'messenger_player_names'
    messenger_id: Mapped[int] = mapped_column(primary_key=True)
    player_uid: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(primary_key=True)
    seen_at: Mapped[CreatedAt]

    messenger_player: Mapped[MessengerPlayer] = relationship(
        back_populates='player_names'
    )

    __table_args__ = (
        CheckConstraint('length(name) > 0', name='name_length'),
        ForeignKeyConstraint(
            ['messenger_id', 'player_uid'],
            ['messenger_players.messenger_id', 'messenger_players.player_uid'],
            ondelete='CASCADE',
        )
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.name!r}, '
            f'seen_at={self.seen_at!r}'
            f')'
        )