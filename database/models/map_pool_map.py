from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from . import MapPool

class MapPoolMap(Base):
    """Represents a map which belongs to a map pool."""

    __tablename__ = 'map_pool_maps'
    map_pool_id: Mapped[int] = mapped_column(
        ForeignKey('map_pools.id', ondelete='CASCADE'),
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(20), primary_key=True)

    map_pool: Mapped[MapPool] = relationship(back_populates='maps')

    __table_args__ = (
        CheckConstraint('length(name) BETWEEN 1 and 20', name='map_name_length'),
    )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'id={self.map_pool_id!r}, '
            f'name={self.name!r}'
            f')'
        )