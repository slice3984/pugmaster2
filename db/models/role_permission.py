from sqlalchemy import BigInteger, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from db.base import Base


class RolePermission(Base):
    """ORM model representing the binding of roles and permissions."""
    __tablename__ = "role_permissions"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    role_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    permission_key: Mapped[str] = mapped_column(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ['guild_id', 'role_id'],
            ['guild_role_permissions.guild_id', 'guild_role_permissions.role_id'],
            ondelete='CASCADE'
        ),
        ForeignKeyConstraint(
            ['permission_key'],
            ['permissions.permission'],
        )
    )

    guild_role: Mapped['GuildRolePermission'] = relationship(back_populates='role_permissions')
    permission: Mapped['Permission'] = relationship(back_populates='role_permissions')