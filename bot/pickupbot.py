from typing import cast

import discord
from discord import Guild, app_commands
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncEngine

from bot.cogs.base_cog import BaseCog
from bot.cogs.guild_configuration import GuildConfiguration
from bot.cogs.permission import Permission
from bot.cogs.ping import Ping
from core.dto.guild_info import GuildInfo
from core.dto.manager_context import ManagerContext
from db.init_tables import init_db
from domain.types import GuildId
from managers.command_access_manager import PermissionScope

dev = True

class PickupBot(commands.Bot):
    def __init__(self,
                 *,
                 manager_context: ManagerContext,
                 engine: AsyncEngine,
                 **kwargs):
        super().__init__(**kwargs)
        self._managers = manager_context
        self._engine = engine
        self._gated_commands: list[str] = []

    async def setup_hook(self) -> None:
        await self.add_cog(Ping(self))
        await self.add_cog(GuildConfiguration(self))
        await self.add_cog(Permission(self))

        if dev:
            DEV_GUILD_ID = 1467241111402840299
            guild = discord.Object(id=DEV_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

        gated_commands = set()

        # Store gated command names
        # Slash cmds
        for cog in self.cogs.values():
            cog = cast(BaseCog, cog)

            for cmd in cog.walk_commands():
                if cog.permission_scope == PermissionScope.GATED:
                    gated_commands.add(cmd.qualified_name)

        # Slash and Hybrid
        for cmd in self.tree.walk_commands():
            if not isinstance(cmd, app_commands.Command):
                continue

            cog_obj = cmd.binding
            if cog_obj is None:
                continue

            cog = cast(BaseCog, cog_obj)

            if cog.permission_scope == PermissionScope.GATED:
                root = cmd
                parent = root.parent

                while parent is not None:
                    root = parent
                    parent = root.parent

                gated_commands.add(root.name)

        self._gated_commands = list(gated_commands)

        await init_db(self._engine, self._gated_commands)

    async def on_ready(self) -> None:
        print(f'Logged in as {self.user} (ID: {self.user.id})')

        await self._managers.guild_state_manager.register_guilds(
            [GuildInfo(guild_id=GuildId(guild.id), name=guild.name) for guild in self.guilds]
        )

        guild = self._managers.guild_state_manager.get_guild_state(GuildId(1467241111402840299))
        print(f'Guild: {guild.settings.prefix}')

    async def on_guild_available(self, guild: Guild) -> None:
        await self._managers.guild_state_manager.register_guild(
            GuildInfo(
                guild_id=GuildId(guild.id),
                name=guild.name
            )
        )

    async def on_guild_join(self, guild: Guild) -> None:
        await self._managers.guild_state_manager.register_guild(
            GuildInfo(
                guild_id=GuildId(guild.id),
                name=guild.name)
        )

    async def on_guild_remove(self, guild: Guild) -> None:
        await self._managers.guild_state_manager.evict_guild(GuildId(guild.id))
        # TODO: Clear states in db

    async def close(self) -> None:
        await super().close()
        await self._engine.dispose()

    @property
    def managers(self):
        return self._managers

    @property
    def gated_commands(self):
        return self._gated_commands
