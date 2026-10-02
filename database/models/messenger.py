from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from enums import MessengerType

if TYPE_CHECKING:
    from . import Community, MessengerPlayer

class Messenger(Base):
    """Represents a messenger which belongs to a community."""

    __tablename__ = 'messengers'
    id: Mapped[int] = mapped_column(primary_key=True)
    community_id: Mapped[int] = mapped_column(ForeignKey('communities.id', ondelete='CASCADE'))
    server_uid: Mapped[str]
    name: Mapped[str]
    messenger_type: Mapped[MessengerType]
    prefix: Mapped[str] = mapped_column(String(5), server_default='!')
    queue_channel_uid: Mapped[str | None]
    moderation_channel_uid: Mapped[str | None]

    community: Mapped[Community] = relationship(back_populates='messengers')

    messenger_players: Mapped[list[MessengerPlayer]] = relationship(
        back_populates='messenger',
        cascade='all',
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint('length(prefix) > 0', name='prefix_length'),
        UniqueConstraint('server_uid', 'messenger_type')
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'messenger_type={self.messenger_type.value!r}, '
            f'prefix={self.prefix!r}'
            f')'
        )