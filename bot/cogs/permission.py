from typing import TYPE_CHECKING, Callable, Literal, cast

import discord
from discord import app_commands, InteractionResponse

from bot.cogs.base_cog import BaseCog
from bot.ui.embeds.permission_embed_factory import PermissionEmbedFactory
from domain.types import GuildId, RoleId
from managers.command_access_manager import ChannelScope, PermissionScope

if TYPE_CHECKING:
    from bot.pickupbot import PickupBot

class Permission(BaseCog):
    channel_scope = ChannelScope.PICKUP_LISTEN
    permission_scope = PermissionScope.GATED

    def __init__(self, bot: PickupBot):
        super().__init__(bot)

    permission = app_commands.Group(
        name="permission",
        description="Role permission management"
    )

    @staticmethod
    def make_command_name_autocomplete(
            mode: Literal["add", "remove"],
    ) -> Callable[[discord.Interaction, str], "discord.utils.MISSING"]:
        async def autocomplete(interaction: discord.Interaction, current: str):
            current_lc = current.lower()

            # Already entered commands
            passed_commands_history = {
                str(value).lower()
                for name, value in vars(interaction.namespace).items()
                if name.startswith("command_") and value is not None
            }

            role = getattr(interaction.namespace, "role", None)
            if interaction.guild_id is None or role is None:
                return []

            bot = cast('PickupBot', interaction.client)
            state = bot.managers.guild_state_manager.get_guild_state(interaction.guild_id)

            if not bot.managers.command_access_manager.has_command_permission(
                    command_name='permission',
                    guild_id=interaction.guild.id,
                    role_ids=[role.id for role in interaction.user.roles],
                    is_admin=interaction.user.guild_permissions.administrator
            ):
                return [app_commands.Choice(name='Unauthorized', value='Unauthorized')]

            role_existing = {c.lower() for c in state.role_command_permissions.get(role.id, [])}

            if mode == "add":
                valid_commands = bot.gated_commands

                candidates = [
                    cmd for cmd in valid_commands
                    if current_lc in cmd.lower()
                       and cmd.lower() not in passed_commands_history
                       and cmd.lower() not in role_existing
                ]

                candidates.sort(key=lambda n: (not n.lower().startswith(current_lc), n.lower()))
                return [app_commands.Choice(name=n, value=n) for n in candidates[:25]]

            # Remove
            candidates = [
                cmd for cmd in role_existing
                if current_lc in cmd and cmd not in passed_commands_history
            ]
            candidates.sort(key=lambda n: (not n.startswith(current_lc), n))
            return [app_commands.Choice(name=n, value=n) for n in candidates[:25]]

        return autocomplete

    @BaseCog.require_slash()
    @permission.command(name='add', description='Add permissions to a role')
    @app_commands.autocomplete(
        command_one=make_command_name_autocomplete(mode='add'),
        command_two=make_command_name_autocomplete(mode='add'),
        command_three=make_command_name_autocomplete(mode='add'),
        command_four=make_command_name_autocomplete(mode='add'),
        command_five=make_command_name_autocomplete(mode='add'),
        command_six=make_command_name_autocomplete(mode='add'),
        command_seven=make_command_name_autocomplete(mode='add'),
        command_eight=make_command_name_autocomplete(mode='add'),
        command_nine=make_command_name_autocomplete(mode='add')
    )
    async def permission_add(
            self,
            interaction: discord.Interaction,
            role: discord.Role,
            command_one: str,
            command_two: str | None = None,
            command_three: str | None = None,
            command_four: str | None = None,
            command_five: str | None = None,
            command_six: str | None = None,
            command_seven: str | None = None,
            command_eight: str | None = None,
            command_nine: str | None = None
    ):
        response: InteractionResponse = interaction.response

        commands = [
            command_one, command_two, command_three, command_four, command_five,
            command_six, command_seven, command_eight, command_nine
        ]

        result = await self.bot.managers.guild_state_manager.add_role_permissions(
            guild_id=interaction.guild.id,
            role_id=role.id,
            command_names=[c for c in commands if c is not None],
            valid_command_names=self.bot.gated_commands
        )

        await response.send_message(
            embed=PermissionEmbedFactory.from_permission_modification(
                mode='add',
                role_name=role.name,
                affected_commands=result
            ),
            ephemeral=True
        )

    @BaseCog.require_slash()
    @permission.command(name='remove', description='Remove permissions from a role')
    @app_commands.autocomplete(
        command_one=make_command_name_autocomplete(mode='remove'),
        command_two=make_command_name_autocomplete(mode='remove'),
        command_three=make_command_name_autocomplete(mode='remove'),
        command_four=make_command_name_autocomplete(mode='remove'),
        command_five=make_command_name_autocomplete(mode='remove'),
        command_six=make_command_name_autocomplete(mode='remove'),
        command_seven=make_command_name_autocomplete(mode='remove'),
        command_eight=make_command_name_autocomplete(mode='remove'),
        command_nine=make_command_name_autocomplete(mode='remove')
    )
    async def permission_remove(
            self,
            interaction: discord.Interaction,
            role: discord.Role,
            command_one: str,
            command_two: str | None = None,
            command_three: str | None = None,
            command_four: str | None = None,
            command_five: str | None = None,
            command_six: str | None = None,
            command_seven: str | None = None,
            command_eight: str | None = None,
            command_nine: str | None = None
    ):
        response: InteractionResponse = interaction.response
        commands = [
            command_one, command_two, command_three, command_four, command_five,
            command_six, command_seven, command_eight, command_nine
        ]

        result = await self.bot.managers.guild_state_manager.remove_role_permissions(
            guild_id=interaction.guild.id,
            role_id=role.id,
            command_names=[c for c in commands if c is not None],
            valid_command_names=self.bot.gated_commands
        )

        await response.send_message(
            embed=PermissionEmbedFactory.from_permission_modification(
                mode='remove',
                role_name=role.name,
                affected_commands=result
            ),
            ephemeral=True
        )

    async def autocomplete_permission_roles(
            group: app_commands.Group,
            interaction: discord.Interaction,
            current: str
    ) -> list[app_commands.Choice[str]]:
        curren_lc = current.lower()

        bot = cast('PickupBot', interaction.client)

        if not bot.managers.command_access_manager.has_command_permission(
            command_name=group.qualified_name.lower(),
            guild_id=interaction.guild.id,
            role_ids=[role.id for role in interaction.user.roles],
            is_admin=interaction.user.guild_permissions.administrator
        ):
            return [app_commands.Choice(name='Unauthorized', value='Unauthorized')]

        state = bot.managers.guild_state_manager.get_guild_state(interaction.guild_id)


        elevated_roles = list(state.role_command_permissions.keys())
        choices: list[app_commands.Choice[str]] = []


        stale_role_ids: list[RoleId] = []
        for role_id in elevated_roles:
            # Try to fetch the role, if its None -> Stale, remove from cache/db
            role = interaction.guild.get_role(role_id)

            if role is None:
                # Stale, remove
                stale_role_ids.append(role_id)
                continue

            if curren_lc and curren_lc not in role.name.lower():
                continue

            choices.append(
                app_commands.Choice(
                    name=role.name,
                    value=role.name,
                )
            )

            if len(choices) > 25:
                break

        if stale_role_ids:
            await bot.managers.guild_state_manager.remove_elevated_roles(
                guild_id=interaction.guild.id,
                role_ids=stale_role_ids,
            )

        return choices

    @BaseCog.require_slash()
    @permission.command(name='show', description='Show permissions assigned to a specific role or all roles')
    @app_commands.autocomplete(role_name=autocomplete_permission_roles)
    async def permission_show(
            self,
            interaction: discord.Interaction,
            role_name: str | None = None,
    ):
        response: InteractionResponse = interaction.response
        state = self.get_guild_state(GuildId(interaction.guild.id))
        elevated_roles = state.role_command_permissions
        roles: dict[str, set[str]] = {}

        if role_name:
            # It is possible that multiple roles have the same name
            for role in interaction.guild.roles:
                if role.name.lower() == role_name.lower():
                    cached_role = elevated_roles.get(RoleId(role.id))

                    if cached_role is not None:
                        roles[role.name] = cached_role
        else:
            stale_role_ids: list[RoleId] = []

            for role_id, permissions in elevated_roles.items():
                role = interaction.guild.get_role(role_id)

                if role is None:
                    stale_role_ids.append(role_id)
                    continue

                roles[role.name] = permissions

            if stale_role_ids:
                await self.bot.managers.guild_state_manager.remove_elevated_roles(
                    guild_id=interaction.guild.id,
                    role_ids=stale_role_ids
                )

        await response.send_message(
            embed=PermissionEmbedFactory.role_permissions(roles, single_role=role_name is not None),
            ephemeral=True
        )