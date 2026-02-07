import discord
from discord import Guild
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncEngine

from bot.cogs.guild_configuration import GuildConfiguration
from bot.cogs.ping import Ping
from core.dto.guild_info import GuildInfo
from core.service_context import ServiceContext
from db.init_tables import init_tables
from domain.types import GuildId

dev = True

class PickupBot(commands.Bot):
    def __init__(self,
                 *,
                 service_context: ServiceContext,
                 engine: AsyncEngine,
                 **kwargs):
        super().__init__(**kwargs)
        self._service_context = service_context
        self._engine = engine

    async def setup_hook(self) -> None:
        await init_tables(self._engine)
        await self.add_cog(Ping(self))
        await self.add_cog(GuildConfiguration(self))

        if dev:
            DEV_GUILD_ID = 1467241111402840299
            guild = discord.Object(id=DEV_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def on_ready(self) -> None:
        print(f'Logged in as {self.user} (ID: {self.user.id})')

        await self._service_context.guild_registry_service.register_guilds(
            [GuildInfo(guild_id=GuildId(guild.id), name=guild.name) for guild in self.guilds]
        )

        guild = self._service_context.guild_registry_service.get_guild_state(GuildId(1467241111402840299))
        print(f'Guild: {guild.settings.prefix}')

    async def on_guild_available(self, guild: Guild) -> None:
        await self._service_context.guild_registry_service.register_guild(
            GuildInfo(
                guild_id=GuildId(guild.id),
                name=guild.name
            )
        )

    async def on_guild_join(self, guild: Guild) -> None:
        await self._service_context.guild_registry_service.register_guild(
            GuildInfo(
                guild_id=GuildId(guild.id),
                name=guild.name)
        )

    async def on_guild_remove(self, guild: Guild) -> None:
        await self._service_context.guild_registry_service.evict_guild(GuildId(guild.id))
        # TODO: Clear states in db

    async def close(self) -> None:
        await super().close()
        await self._engine.dispose()

    @property
    def service_context(self):
        return self._service_context
