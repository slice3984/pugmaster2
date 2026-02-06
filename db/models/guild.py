from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base

class Guild(Base):
    """ORM model representing a guild."""
    __tablename__ = 'guilds'

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    prefix: Mapped[str] = mapped_column(Text(10), nullable=False, default='!')
    pickup_channel_id: Mapped[int | None] = mapped_column(BigInteger)
    listen_channel_id: Mapped[int | None] = mapped_column(BigInteger)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )