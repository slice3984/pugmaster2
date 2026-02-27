from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class QueueConfigModel(Base):
    """ORM model representing settings for a guild queue"""
    __tablename__ = 'queue_configs'

    guild_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('guilds.guild_id', ondelete='CASCADE'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    player_count: Mapped[int] = mapped_column()
    team_count: Mapped[int] = mapped_column()

    __table_args__ = (
        UniqueConstraint('guild_id','name', name='uq_queue_configs_guild_name'),
    )

