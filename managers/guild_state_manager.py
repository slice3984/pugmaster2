import asyncio
from dataclasses import replace
from typing import Iterable

from core.dto.guild_config_update_result import GuildConfigUpdateResult
from core.dto.guild_info import GuildInfo
from domain.guild_state import GuildState, GuildSettings
from domain.types import GuildId
from services.guild_repository_service import GuildRepositoryService, GuildNotCachedError
from services.guild_state_cache import GuildStateCache

class GuildStateManager:
    def __init__(self, guild_repository_service: GuildRepositoryService) -> None:
        self._cache = GuildStateCache()
        self._repository_service = guild_repository_service
        self._locks: dict[GuildId, asyncio.Lock] = {}

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
            self._cache[guild.guild_id] = GuildState(settings=guild_settings)

    async def register_guilds(self, guilds: Iterable[GuildInfo]) -> None:
        for guild in guilds:
            await self.register_guild(guild)

    async def update_guild_config(self, guild_settings: GuildSettings) -> GuildConfigUpdateResult:
        """Updates guild settings in database and cache."""
        if self._cache[guild_settings.guild_id] is None:
            raise GuildNotCachedError(f'Guild {guild_settings.guild_id} not cached')

        if guild_settings.listen_channel_id == guild_settings.pickup_channel_id:
            return GuildConfigUpdateResult(
                ok=False,
                settings=None,
                error='Pickup and Listen channel should differ from each other.'
            )

        lock = self._locks.setdefault(guild_settings.guild_id, asyncio.Lock())
        async with lock:
            curr_state = self._cache[guild_settings.guild_id]

            if curr_state is None:
                raise GuildNotCachedError(f'Guild {guild_settings.guild_id} not cached')

            updated = await self._repository_service.update_guild_settings(guild_settings=guild_settings)

            if not updated:
                return GuildConfigUpdateResult(
                    ok=False,
                    settings=None,
                    error='Something went wrong updating the database.'
                )

            new_settings = replace(
                curr_state.settings,
                pickup_channel_id=guild_settings.pickup_channel_id,
                listen_channel_id=guild_settings.listen_channel_id
            )

            new_state = replace(curr_state, settings=new_settings)
            self._cache[guild_settings.guild_id] = new_state

            return GuildConfigUpdateResult(ok=True, settings=new_settings, error=None)

    def get_guild_state(self, guild_id: GuildId) -> GuildState:
        state = self._cache[guild_id]

        if state is None:
            raise GuildNotCachedError(f'Guild {guild_id} not cached')

        return state

    async def evict_guild_state(self, guild_id: GuildId) -> None:
        lock = self._locks.setdefault(guild_id, asyncio.Lock())
        async with lock:
            if self._cache[guild_id] is not None:
                del self._cache[guild_id]