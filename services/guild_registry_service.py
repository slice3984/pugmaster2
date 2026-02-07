import asyncio
from dataclasses import replace
from os import name
from typing import List, Iterable, cast

from sqlalchemy import update, CursorResult
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from core.dto.guild_info import GuildInfo
from db.models.guild import Guild
from domain.guild_state import GuildState, GuildSettings
from domain.types import GuildId
from services.guild_state_cache import GuildStateCache

class GuildNotCachedError(RuntimeError):
    pass

class GuildRegistryService:
    """Updates, deletes and creates guild state, communicates with the database."""

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sessionmaker = sessionmaker
        self._locks: dict[int, asyncio.Lock] = {}
        self._guild_state_cache: GuildStateCache = GuildStateCache()

    async def register_guild(self, guild: GuildInfo) -> None:
        # Check the cache first
        if self._guild_state_cache[guild.guild_id] is not None:
            return

        lock = self._locks.setdefault(guild.guild_id, asyncio.Lock())

        async with lock:
            if self._guild_state_cache[guild.guild_id] is not None:
                return

            async with self._sessionmaker() as session:
                try:
                    async with session.begin():
                        db_guild = await session.get(Guild, guild.guild_id)

                        if db_guild is None:
                            session.add(Guild(guild_id=guild.guild_id, name=guild.name))

                        self._guild_state_cache[guild.guild_id] = GuildState(
                            settings=GuildSettings(
                                guild_id=guild.guild_id,
                                prefix=db_guild.prefix if db_guild is not None else '!'
                            )
                        )
                except IntegrityError:
                    pass

    async def register_guilds(self, guilds: Iterable[GuildInfo]) -> None:
        for guild in guilds:
            await self.register_guild(guild)

    async def update_guild_state(self, guild_settings: GuildSettings) -> GuildState:
        """Updates guild settings state in cache and database."""
        if self._guild_state_cache[guild_settings.guild_id] is None:
            raise GuildNotCachedError(f"{guild_settings.guild_id} not cached")

        lock = self._locks.setdefault(guild_settings.guild_id, asyncio.Lock())
        async with lock:
            curr_state = self._guild_state_cache[guild_settings.guild_id]

            if curr_state is None:
                raise GuildNotCachedError(f"{guild_settings.guild_id} not cached")

            async with self._sessionmaker() as session:
                async with session.begin():
                    # Update database
                    stmt = (
                        update(Guild)
                        .where(Guild.guild_id == guild_settings.guild_id)
                        .values(
                            pickup_channel_id=guild_settings.pickup_channel_id,
                            listen_channel_id=guild_settings.listen_channel_id
                        )
                    )

                    result: Result = await session.execute(stmt)
                    cursor_result = cast(CursorResult, result)

                    # In case the dbms did not update any data, should not happen
                    if cursor_result.rowcount == 0:
                        return curr_state

                    # Update cache, atomic update
                    new_settings = replace(
                        curr_state.settings,
                        pickup_channel_id=guild_settings.pickup_channel_id,
                        listen_channel_id=guild_settings.listen_channel_id
                    )

                    new_state = replace(curr_state, settings=new_settings)
                    self._guild_state_cache[guild_settings.guild_id] = new_state

                    return new_state

    def get_guild_state(self, guild_id: GuildId) -> GuildState:
        return self._guild_state_cache[guild_id]

    async def evict_guild(self, guild_id: GuildId) -> None:
        if self._guild_state_cache[guild_id] is None:
            return

        del self._guild_state_cache[guild_id]
