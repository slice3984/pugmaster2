from enum import Enum, auto
from typing import TYPE_CHECKING
import discord
from discord.ext import commands
from domain.guild_state import GuildState
from domain.types import GuildId
from managers.command_access_manager import ChannelScope, PermissionScope
from services.guild_repository_service import GuildNotCachedError

if TYPE_CHECKING:
    from bot.pickupbot import PickupBot

class BaseCog(commands.Cog):
    """
    Base class for all cogs.
        - Channels can be gated using the class attribute `channel_scope`
        - Permissions can be enforced using the class attribute `permission_scope`
    """

    channel_scope: ChannelScope = ChannelScope.PICKUP
    permission_scope: PermissionScope = PermissionScope.EVERYONE

    def __init__(self, bot: PickupBot) -> None:
        self.bot = bot

    def get_guild_state(self, guild_id: GuildId) -> GuildState:
        state = self.bot.managers.guild_state_manager.get_guild_state(GuildId(guild_id))

        if state is None:
            raise GuildNotCachedError(guild_id)

        return state

    async def cog_check(self, ctx: commands.Context) -> bool:
        # Direct messages
        if ctx.guild is None or ctx.channel.type != discord.ChannelType.text:
            return False

        if not self.bot.managers.command_access_manager.check_channel_scope(
            required_scope=self.channel_scope,
            guild_id=ctx.guild.id,
            current_channel_id=ctx.channel.id
        ):
            return False

        if not self.bot.managers.command_access_manager.check_permission_scope(
            required_scope=self.permission_scope,
            guild_member_role_ids=[ role.id for role in ctx.author.roles ],
            is_admin=ctx.author.guild_permissions.administrator,
            command_name=self.qualified_name
        ):
            return False

        return True