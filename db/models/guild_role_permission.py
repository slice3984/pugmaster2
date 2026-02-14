from typing import List

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from db.base import Base


class GuildRolePermission(Base):
    """ORM model representing guild role permissions."""
    __tablename__ = "guild_role_permissions"

    guild_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('guilds.guild_id', ondelete='CASCADE'),
        primary_key=True
    )

    role_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    role_permissions: Mapped[List['RolePermission']] = relationship(
        back_populates='guild_role',
        cascade='all, delete-orphan'
    )

