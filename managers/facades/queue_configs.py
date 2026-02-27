from dataclasses import dataclass
from typing import Collection, TYPE_CHECKING, Iterable

from core.dto.queue_config import QueueConfig
from domain.guild_state import QueueState
from domain.types import GuildId
from managers.logic import queue_config
from managers.logic.queue_config import QueueCreationData, RemoveQueuesPlan

if TYPE_CHECKING:
    from managers.guild_state_manager import GuildStateManager

@dataclass(frozen=True)
class CreateQueuesResult:
    added_queues: frozenset[QueueCreationData]
    errors: dict[str, list[str]]

class QueueConfigsFacade:
    def __init__(self, guild_state_manager: GuildStateManager):
        self._sm = guild_state_manager

    async def create_queues(
            self,
            guild_id: GuildId,
            queues: Collection[QueueCreationData]
    ) -> CreateQueuesResult:
        async with self._sm.acquire_lock(guild_id=guild_id):
            state = self._sm._require_state(guild_id=guild_id)

            plan = queue_config.plan_create_queues(
                state=state,
                queues=queues,
            )

            if plan.to_add:
                queue_configs: list[QueueConfig] = await self._sm._queue_service.create_queues(
                    guild_id=guild_id,
                    queues=plan.to_add
                )

                # Update cache
                guild_queues = dict(state.queues)

                for qc in queue_configs:
                    guild_queues[qc.name] = QueueState(
                        queue_config=qc,
                        player_ids=set()
                    )

                self._sm._mutate_state(guild_id, 'queues', guild_queues)

            return CreateQueuesResult(
                added_queues=plan.to_add,
                errors=plan.errors
            )

    def preview_remove_queues(
            self,
            guild_id: GuildId,
            queues: Iterable[str]
    ) -> RemoveQueuesPlan:
        # Returns the current queue removal plan, has to be rechecked on actual removal, as the state could be invalid
        return queue_config.plan_remove_queues(
            state=self._sm._require_state(guild_id=guild_id),
            queue_names=queues
        )

    async def apply_remove_queues(
            self,
            guild_id: GuildId,
            queues: Iterable[str]
    ) -> RemoveQueuesPlan:
        # TODO: Queue state handling
        async with self._sm.acquire_lock(guild_id=guild_id):
            state = self._sm._require_state(guild_id=guild_id)

            # Recheck
            plan = self.preview_remove_queues(guild_id=guild_id, queues=queues)

            if plan.to_remove:
                await self._sm._queue_service.remove_queues(
                    guild_id=guild_id,
                    queues=plan.to_remove
                )

                # Cache
                cached_queues = dict(state.queues)

                for queue_to_remove in plan.to_remove:
                    cached_queues.pop(queue_to_remove, None)

                self._sm._mutate_state(guild_id, 'queues', cached_queues)

            return plan