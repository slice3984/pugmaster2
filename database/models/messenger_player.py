from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, true, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from . import CommunityPlayer, Messenger, MessengerPlayerName

class MessengerPlayer(Base):
    """Represents a user of a messenger, stores player specific settings.
    MessengerPlayers are merged as a CommunityPlayer.
    """

    __tablename__ = 'messenger_players'
    messenger_id: Mapped[int] = mapped_column(
        ForeignKey('messengers.id', ondelete='CASCADE'),
        primary_key=True
    )
    community_player_id: Mapped[int] = mapped_column(ForeignKey('community_players.id', ondelete='CASCADE'))
    player_uid: Mapped[str] = mapped_column(primary_key=True)
    display_name: Mapped[str]
    notify: Mapped[bool] = mapped_column(server_default=true())

    community_player: Mapped[CommunityPlayer] = relationship(back_populates='messenger_players')
    messenger: Mapped[Messenger] = relationship(back_populates='messenger_players')

    player_names: Mapped[list[MessengerPlayerName]] = relationship(
        back_populates='messenger_player',
        cascade='all',
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint('length(display_name) > 0', name='display_name_length'),
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.display_name!r}, '
            f'display_name={self.display_name!r}, '
            f'notify={self.notify!r}'
            f')'
        )


