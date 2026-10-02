from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from . import CommunityCommandSettings

class CommunityCommandOverride(Base):
    """Represents a given community command override stored as key-value pair."""

    __tablename__ = 'community_command_overrides'
    community_command_settings_id: Mapped[int] = mapped_column(
        ForeignKey('community_command_settings.id', ondelete='CASCADE'),
        primary_key=True
    )
    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]

    command_settings: Mapped[CommunityCommandSettings] = relationship(back_populates='overrides')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'key={self.key!r}, '
            f'value={self.value!r}'
            f')'
        )



