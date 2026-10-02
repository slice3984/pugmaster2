from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from . import Community

from . import Base

class ServerPool(Base):
    """Represents a game server for a community."""

    __tablename__ = 'server_pools'
    id: Mapped[int] = mapped_column(primary_key=True)
    community_id: Mapped[int] = mapped_column(
        ForeignKey('communities.id', ondelete='CASCADE')
    )

    name: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(String(255))

    community: Mapped[Community] = relationship(back_populates='servers')

    __table_args__ = (
        CheckConstraint('length(name) BETWEEN 1 AND 20', 'length_name'),
        CheckConstraint('length(address) BETWEEN 1 AND 255', 'length_address'),
        UniqueConstraint('community_id', 'name')
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'address={self.address!r}'
            f')'
        )