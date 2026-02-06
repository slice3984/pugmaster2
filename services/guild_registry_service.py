import asyncio
from os import name
from typing import List, Iterable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from core.dto.guild_info import GuildInfo
from db.models.guild import Guild
from domain.guild_state import GuildState, GuildSettings
from domain.types import GuildId
from services.guild_state_cache import GuildStateCache


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


    async def get_guild_state(self, guild_id: GuildId) -> GuildState:
        return self._guild_state_cache[guild_id]


    async def evict_guild(self, guild_id: GuildId) -> None:
        if self._guild_state_cache[guild_id] is None:
            return

        del self._guild_state_cache[guild_id]
