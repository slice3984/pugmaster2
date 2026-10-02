from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from . import Community, MapPoolMap, Queue

class MapPool(Base):
    """Represents a map pool which can be used for queues."""

    __tablename__ = 'map_pools'
    id: Mapped[int] = mapped_column(primary_key=True)
    community_id: Mapped[int] = mapped_column(
        ForeignKey('communities.id', ondelete='CASCADE')
    )

    name: Mapped[str] = mapped_column(String(20))
    community: Mapped[Community] = relationship(back_populates='map_pools')

    maps: Mapped[list[MapPoolMap]] = relationship(
        back_populates='map_pool',
        cascade='all',
        passive_deletes=True
    )
    queues: Mapped[list[Queue]] = relationship(
        back_populates='map_pool',
        passive_deletes=True
    )

    __table_args__ = (
        UniqueConstraint('community_id', 'name'),
        CheckConstraint('length(name) BETWEEN 1 and 20', name='pool_name_length'),
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}'
            f')'
        )