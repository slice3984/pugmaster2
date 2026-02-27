import asyncio
from typing import cast, Collection, Iterable

from sqlalchemy import insert, select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from core.dto.queue_config import QueueConfig
from db.models.queue_config import QueueConfigModel
from domain.types import GuildId
from managers.logic.queue_config import QueueCreationData


class GuildQueueService:
    """Handles queue configuration and queue state on database level."""

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sessionmaker = sessionmaker

    """
    CONFIGURATION
    """

    async def create_queues(self, guild_id: GuildId, queues: Collection[QueueCreationData]) -> list[QueueConfig]:
        """Create queues, key: name, value: (player_count, team_count)"""
        async with self._sessionmaker() as session:
            async with session.begin():
                try:
                    stmt = insert(QueueConfigModel).values(
                        [
                            {
                                'guild_id': guild_id,
                                'name': queue.name,
                                'player_count': queue.player_count,
                                'team_count': queue.team_count
                            }
                            for queue in queues
                        ],
                    )

                    await session.execute(stmt)
                except IntegrityError:
                    # Todo: log it
                    return []

        return [
            QueueConfig(name=queue.name, player_count=queue.player_count, team_count=queue.team_count)
            for queue in queues
        ]

    async def fetch_queues(self, guild_id: GuildId) -> list[QueueConfig]:
        """Fetches queue configurations for a guild"""
        fetched_queues: list[QueueConfig] = []

        async with self._sessionmaker() as session:
            async with session.begin():
                stmt = select(QueueConfigModel).where(QueueConfigModel.guild_id == guild_id)
                queues: list[QueueConfigModel] = cast(list[QueueConfigModel], (await session.execute(stmt)).scalars().all())

                for queue in queues:
                    fetched_queues.append(
                        QueueConfig(
                            name=queue.name,
                            player_count=queue.player_count,
                            team_count=queue.team_count
                        )
                    )

        return fetched_queues

    async def remove_queues(self, guild_id: GuildId, queues: Iterable[str]) -> frozenset[str]:
        """Remove queues from a guild"""
        removed_queues: list[str] = []

        async with self._sessionmaker() as session:
            async with session.begin():
                stmt = select(QueueConfigModel).where(
                    QueueConfigModel.guild_id == guild_id,
                    QueueConfigModel.name.in_(queues)
                )

                db_queues = (await session.execute(stmt)).scalars().all()

                for queue in db_queues:
                    removed_queues.append(queue.name)
                    await session.delete(queue)

        return frozenset(removed_queues)
