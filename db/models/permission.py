from typing import List

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from db.base import Base

class Permission(Base):
    """ORM model representing a permission."""
    __tablename__ = 'permissions'
    permission: Mapped[str] = mapped_column(primary_key=True)

    role_permissions: Mapped[List['RolePermission']] = relationship(
        back_populates='permission',
        cascade='all, delete-orphan'
    )