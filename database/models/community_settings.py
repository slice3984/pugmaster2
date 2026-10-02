from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from . import Community

class CommunitySettings(Base):
    """Represents the shared settings for a community."""

    __tablename__ = "community_settings"
    community_id: Mapped[int] = mapped_column(
        ForeignKey('communities.id', ondelete='CASCADE'),
        primary_key=True
    )

    team_a_name: Mapped[str] = mapped_column(String(20), server_default='A')
    team_b_name: Mapped[str] = mapped_column(String(20), server_default='B')

    community: Mapped[Community] = relationship(back_populates='settings')

    __table_args__ = (
        CheckConstraint('team_a_name != team_b_name', name='different_team_names'),
        CheckConstraint('length(team_a_name) BETWEEN 1 AND 20', name='team_a_name_length'),
        CheckConstraint('length(team_b_name) BETWEEN 1 AND 20', name='team_b_name_length')
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'team_a_name={self.team_a_name!r}, '
            f'team_b_name={self.team_b_name!r} '
            f')'
        )