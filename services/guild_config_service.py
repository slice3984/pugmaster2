import asyncio
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from domain.guild_state import GuildSettings
from domain.types import GuildId
from services.guild_registry_service import GuildRegistryService


@dataclass(frozen=True)
class GuildConfigUpdateResult:
    ok: bool
    settings: GuildSettings | None
    error: str | None

class GuildConfigService:
    def __init__(
            self,
            sessionmaker: async_sessionmaker[AsyncSession],
            guild_registry_service: GuildRegistryService
    ) -> None:
        self._sessionmaker = sessionmaker
        self._guild_registry_service = guild_registry_service
        self._locks: dict[GuildId, asyncio.Lock] = {}

    async def update_guild_config(self, guild_settings: GuildSettings) -> GuildConfigUpdateResult:

        if guild_settings.listen_channel_id == guild_settings.pickup_channel_id:
            return GuildConfigUpdateResult(
                ok=False,
                settings=None,
                error='Pickup and Listen channel should differ from each other.'
            )

        guild_state = await self._guild_registry_service.update_guild_state(guild_settings)

        return GuildConfigUpdateResult(ok=True, settings=guild_state.settings, error=None)
