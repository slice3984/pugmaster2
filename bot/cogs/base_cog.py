from typing import TYPE_CHECKING, cast, Callable, Iterable
import discord
from discord import app_commands, Role
from discord.ext import commands

from domain.guild_state import GuildState
from domain.types import GuildId
from managers.logic.command_access import ChannelScope, PermissionScope
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

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply('Unauthorized or wrong channel.', delete_after=8)
            return
        raise error

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            if interaction.response.is_done():
                await interaction.followup.send("Unauthorized or wrong channel.", ephemeral=True)
            else:
                await interaction.response.send_message("Unauthorized or wrong channel.", ephemeral=True)
            return
        raise error

    def _check(
            self,
            guild_id: GuildId,
            current_channel_id: int,
            guild_member_roles: list[Role],
            is_admin: bool,
            command_name: str
    ) -> bool:
        perms = self.bot.managers.guild_state_manager.permissions

        if not perms.check_channel_scope(
                required_scope=self.channel_scope,
                guild_id=guild_id,
                current_channel_id=current_channel_id
        ):
            return False

        if not perms.check_permission_scope(
            required_scope=self.permission_scope,
            guild_id=guild_id,
            role_ids=[role.id for role in guild_member_roles],
            is_admin=is_admin,
            command_name=command_name
        ):
            return False

        return True

    @classmethod
    def require_slash(cls):
        async def predicate(interaction: discord.Interaction):
            # Guild only
            if interaction.guild is None or interaction.channel is None:
                return False

            cog = interaction.command.binding

            if cog is None:
                return False

            cog = cast(BaseCog, cog)

            # Make sure they are a member
            if not isinstance(interaction.user, discord.Member):
                return False

            full_name = getattr(interaction.command, "qualified_name", interaction.command.name)
            command_name = full_name.split(' ', 1)[0]

            return cog._check(
                guild_id=GuildId(interaction.guild.id),
                current_channel_id=interaction.channel.id,
                guild_member_roles=interaction.user.roles,
                is_admin=interaction.user.guild_permissions.administrator,
                command_name=command_name
            )

        return app_commands.check(predicate)

    @classmethod
    def require_cmd(cls):
        async def predicate(ctx: commands.Context):
            cog = ctx.cog

            if cog is None:
                return False

            cog = cast(BaseCog, cog)

            member = ctx.author

            if not isinstance(member, discord.Member):
                return False

            return cog._check(
                guild_id=GuildId(ctx.guild.id),
                current_channel_id=ctx.channel.id,
                guild_member_roles=member.roles,
                is_admin=member.guild_permissions.administrator,
                command_name=ctx.command.qualified_name if ctx.command else "unknown"
            )

        return commands.check(predicate)

    @staticmethod
    def autocompletes_numbered(
            base_name: str,
            amount: int,
            func: Callable[..., Callable],
            **func_kwargs
    ):
        """
        Helper function for numbered autocompletes.
         - Generates numbered autocompletes based on base_name.
         - Example: base_name_one, base_name_two, ...
        """
        number_words = [
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
            'nine', 'ten', 'eleven', 'twelve',
        ]

        mapping = {
            f'{base_name}_{number_words[i]}': func(**func_kwargs)
            for i in range(amount)
        }

        return app_commands.autocomplete(**mapping)

    @staticmethod
    def build_autocomplete_candidates(
            field_current_value: str,
            field_prefix: str,
            interaction: discord.Interaction,
            allowed_values: Iterable[str] | None = None,
            disallowed_values: Iterable[str] | None = None,
    ) -> list[str]:
        """Filters allowed_values by current input and excludes already entered values."""
        current_lc = field_current_value.lower()

        passed_history_lc = {
            str(value).lower()
            for name, value in vars(interaction.namespace).items()
            if name.startswith(field_prefix) and value is not None
        }

        passed_history_lc.discard(field_current_value.lower())
        disallowed_lc = {v.lower() for v in disallowed_values} if disallowed_values else set()

        # Determine base candidate pool
        if allowed_values is not None:
            base_values = allowed_values
        else:
            base_values = disallowed_values or []

        return [
            value
            for value in base_values
            if current_lc in value.lower()
               and value.lower() not in passed_history_lc
               and value.lower() not in disallowed_lc
        ]

    @staticmethod
    def has_autocomplete_permission(
        interaction: discord.Interaction,
        command_permission: str | None,
    ) -> bool:
        """Checks whether the user has permission for the given command."""
        if command_permission is None:
            return True

        guild = interaction.guild
        if guild is None:
            return False

        bot = cast("PickupBot", interaction.client)
        sm = bot.managers.guild_state_manager
        perm = sm.permissions

        member = interaction.user

        return perm.has_command_permission(
            command_name=command_permission,
            guild_id=guild.id,
            role_ids=[r.id for r in getattr(member, "roles", [])],
            is_admin=getattr(
                getattr(member, "guild_permissions", None),
                "administrator",
                False,
            ),
        )