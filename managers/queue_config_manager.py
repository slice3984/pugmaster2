import asyncio

from domain.types import GuildId
from managers.guild_state_manager import GuildStateManager
from services.guild_queue_service import GuildQueueService

class QueueConfigManager:
    def __init__(self, guild_queue_service: GuildQueueService, guild_state_manager: GuildStateManager):
        self._guild_queue_service = guild_queue_service
        self._guild_state_manager = guild_state_manager
        self._locks: dict[GuildId, asyncio.Lock] = {}

    def _filter_queue_names(
            self,
            intersection: bool,
            guild_id: GuildId,
            queue_names: set[str]
    ) -> list[str]:
        state = self._guild_state_manager.get_guild_state(guild_id)

        if intersection:
            return [queue for queue in queue_names if queue in state.queues.keys()]
        else:
            return [queue for queue in queue_names if queue not in state.queues.keys()]

    def create_queues(
            self,
            guild_id: GuildId,
            queues: dict[str, tuple[int, int]]
    ):
        """Create queues, key: name, value: (player_count, team_count)"""
        # Check if queues already exist
        valid_queues = self._filter_queue_names(
            intersection=False,
            guild_id=guild_id,
            queue_names=set(queues.keys())
        )

        print(valid_queues)

        # TODO: Cache check
