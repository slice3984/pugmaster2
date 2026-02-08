import asyncio
from dataclasses import replace
from typing import cast

from sqlalchemy import update, CursorResult
from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from core.dto.guild_info import GuildInfo
from db.models.guild import Guild
from domain.guild_state import GuildState, GuildSettings
from services.guild_state_cache import GuildStateCache

class GuildNotCachedError(RuntimeError):
    pass

class GuildRepositoryService:
    """Updates, deletes and creates guild state, communicates with the database."""

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sessionmaker = sessionmaker
        self._locks: dict[int, asyncio.Lock] = {}
        self._guild_state_cache: GuildStateCache = GuildStateCache()

    async def fetch_guild_settings(self, guild_info: GuildInfo) -> GuildSettings:
        async with self._sessionmaker() as session:
            async with session.begin():
                db_guild = await session.get(Guild, guild_info.guild_id)

                if db_guild is None:
                    db_guild = Guild(guild_id=guild_info.guild_id, name=guild_info.name)
                    session.add(db_guild)

                return GuildSettings(
                    guild_id = guild_info.guild_id,
                    prefix=db_guild.prefix,
                    listen_channel_id=db_guild.listen_channel_id,
                    pickup_channel_id=db_guild.pickup_channel_id
                )

    async def update_guild_settings(self, guild_settings: GuildSettings) -> bool:
        async with self._sessionmaker() as session:
            async with session.begin():
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
                    return False

        return True