import asyncio
from datetime import timedelta, timezone, datetime
from dataclasses import replace
from typing import Iterable

from core.dto.guild_config_update_result import GuildConfigUpdateResult
from core.dto.guild_info import GuildInfo
from domain.guild_state import GuildState, GuildSettings, QueueState, GuildStateField, ActiveGuildPrompt
from domain.types import GuildId, RoleId
from managers.facades.permissions import PermissionsFacade
from managers.facades.queue_configs import QueueConfigsFacade
from services.guild_queue_service import GuildQueueService
from services.guild_repository_service import GuildRepositoryService, GuildNotCachedError
from services.guild_state_cache import GuildStateCache


class GuildStateManager:
    def __init__(self, guild_repository_service: GuildRepositoryService, guild_queue_service: GuildQueueService) -> None:
        self._cache = GuildStateCache()
        self._repository_service = guild_repository_service
        self._queue_service = guild_queue_service
        self._locks: dict[GuildId, asyncio.Lock] = {}

        # Facades
        self.permissions = PermissionsFacade(self)
        self.queue_configs = QueueConfigsFacade(self)

    def acquire_lock(self, guild_id: GuildId) -> asyncio.Lock:
        return self._locks.setdefault(guild_id, asyncio.Lock())

    def _require_state(self, guild_id: GuildId) -> GuildState:
        state = self._cache[guild_id]

        if state is None:
            raise GuildNotCachedError(f'Guild {guild_id} not cached')

        return state

    def _mutate_state(self, guild_id: GuildId, field: GuildStateField, value) -> GuildState:
        state = self._require_state(guild_id)
        new_state = replace(state, **{field: value})  # type: ignore[misc]
        self._cache[guild_id] = new_state

        return new_state

    async def register_guild(self, guild: GuildInfo) -> None:
        """Loads and caches guild state if necessary."""
        # Only register if not in cache
        if self._cache[guild.guild_id] is not None:
            return

        lock = self._locks.setdefault(guild.guild_id, asyncio.Lock())

        async with lock:
            if self._cache[guild.guild_id] is not None:
                return

            guild_settings = await self._repository_service.fetch_guild_settings(guild_info=guild)
            guild_role_permissions = await self._repository_service.fetch_guild_role_permissions(guild_id=guild.guild_id)
            guild_queue_configs = await self._queue_service.fetch_queues(guild_id=guild.guild_id)

            self._cache[guild.guild_id] = GuildState(
                settings=guild_settings,
                role_command_permissions=guild_role_permissions,
                queues= {
                    config.name: QueueState(
                        queue_config=config, player_ids=set()
                    )
                    for config in guild_queue_configs
                }
            )

    async def register_guilds(self, guilds: Iterable[GuildInfo]) -> None:
        for guild in guilds:
            await self.register_guild(guild)

    async def update_guild_config(self, guild_settings: GuildSettings) -> GuildConfigUpdateResult:
        """Updates guild settings in database and cache."""
        if guild_settings.listen_channel_id == guild_settings.pickup_channel_id:
            return GuildConfigUpdateResult(
                ok=False,
                settings=None,
                error='Pickup and Listen channel should differ from each other.'
            )

        lock = self._locks.setdefault(guild_settings.guild_id, asyncio.Lock())
        async with lock:
            state = self._require_state(guild_settings.guild_id)
            updated = await self._repository_service.update_guild_settings(guild_settings=guild_settings)

            if not updated:
                return GuildConfigUpdateResult(
                    ok=False,
                    settings=None,
                    error='Something went wrong updating the database.'
                )

            new_settings = replace(
                state.settings,
                pickup_channel_id=guild_settings.pickup_channel_id,
                listen_channel_id=guild_settings.listen_channel_id
            )

            new_state = replace(state, settings=new_settings)
            self._cache[guild_settings.guild_id] = new_state

            return GuildConfigUpdateResult(ok=True, settings=new_settings, error=None)

    def get_guild_state(self, guild_id: GuildId) -> GuildState:
        return self._require_state(guild_id)

    async def evict_guild_state(self, guild_id: GuildId) -> None:
        lock = self._locks.setdefault(guild_id, asyncio.Lock())
        async with lock:
            if self._cache[guild_id] is not None:
                del self._cache[guild_id]

    def try_acquire_prompt_lease(self,
                          guild_id: GuildId,
                          prompt_type: ActiveGuildPrompt
    ) -> bool:
        """Attempts to lock a prompt, if in use returns False, on TTL expiration relocks."""
        state = self._require_state(guild_id)
        prompt_locks = state.active_prompts

        TTL = 300 # Seconds
        prompt_lock = prompt_locks.get(prompt_type, None)

        if prompt_lock is None:
            prompt_locks[prompt_type] = datetime.now(timezone.utc)
            return True

        # TTL
        if datetime.now(timezone.utc) - prompt_lock > timedelta(seconds=TTL):
            prompt_locks[prompt_type] = datetime.now(timezone.utc)
            return True

        return False

    def release_prompt_lease(self, guild_id: GuildId, prompt_type: ActiveGuildPrompt):
        state = self._require_state(guild_id)
        state.active_prompts.pop(prompt_type, None)