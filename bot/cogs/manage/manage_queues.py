import re
from typing import TYPE_CHECKING, Callable, cast

import discord
from discord import app_commands, InteractionResponse

from bot.cogs.base_cog import BaseCog
from bot.ui.embeds.queues_config_embed_factory import QueuesConfigEmbedFactory
from bot.ui.embeds.views.confirm_remove_queues import ConfirmRemoveQueuesView
from managers.logic.command_access import ChannelScope, PermissionScope
from managers.logic.queue_config import QueueCreationData, RemoveQueuesPlan

if TYPE_CHECKING:
    from bot.pickupbot import PickupBot

class ManageQueues(BaseCog):
    channel_scope = ChannelScope.PICKUP_LISTEN
    permission_scope = PermissionScope.GATED

    def __init__(self, bot: PickupBot):
        super().__init__(bot)

    manage_queues = app_commands.Group(
        name="manage_queues",
        description="Queue management"
    )

    @BaseCog.require_slash()
    @manage_queues.command(name="create", description="Each queue is separated by a space, team count is optional, syntax: name:player_count:team_count ...")
    async def create_queues(
        self,
        interaction: discord.Interaction,
        queues: str
    ):
        response: InteractionResponse = interaction.response

        sanitized_queues_str = re.findall(r'\w+:\d{1,3}(?::\d{1,2})?', queues)

        if len(sanitized_queues_str) == 0:
            return await response.send_message(
                embed=QueuesConfigEmbedFactory.no_valid_queues_provided(),
                ephemeral=True
            )

        if len(sanitized_queues_str) > 10:
            return await response.send_message(embed=QueuesConfigEmbedFactory.exceeded_creation_limit(), ephemeral=True)

        queues: list[QueueCreationData] = []

        for queue_str in sanitized_queues_str:
            parts = queue_str.split(':')

            if len(parts) == 2:
                name = parts[0]
                player_count = int(parts[1])
                team_count = 2
            else:
                name, player_count, team_count = parts[0], int(parts[1]), int(parts[2])

            queues.append(QueueCreationData(name=name, player_count=player_count, team_count=team_count))

        result = await self.bot.managers.guild_state_manager.queue_configs.create_queues(
            guild_id=interaction.guild.id,
            queues=queues
        )

        await response.send_message(
            embed=QueuesConfigEmbedFactory.create_queues(result),
            ephemeral=True
        )

    @staticmethod
    def make_queue_name_autocomplete() -> Callable[[discord.Interaction, str], "discord.utils.MISSING"]:
        async def autocomplete(interaction: discord.Interaction, current: str):
            current_lc = current.lower()

            if not BaseCog.has_autocomplete_permission(
                    interaction=interaction,
                    command_permission="manage_queues",
            ):
                return [app_commands.Choice(name="Unauthorized", value="Unauthorized")]

            bot = cast('PickupBot', interaction.client)
            sm = bot.managers.guild_state_manager
            state = sm.get_guild_state(interaction.guild.id)

            candidates = BaseCog.build_autocomplete_candidates(
                field_current_value=current,
                field_prefix="queue_",
                allowed_values={q.queue_config.name for q in state.queues.values()},
                interaction=interaction,
            )

            candidates.sort(key=lambda q: (not q.lower().startswith(current_lc), q.lower()))

            return [app_commands.Choice(name=n, value=n) for n in candidates[:25]]

        return autocomplete

    @BaseCog.require_slash()
    @manage_queues.command(name="remove", description="Remove stored queues")
    @BaseCog.autocompletes_numbered(
        base_name='queue',
        amount=9,
        func=make_queue_name_autocomplete
    )
    async def remove_queues(
            self,
            interaction: discord.Interaction,
            queue_one: str,
            queue_two: str | None,
            queue_three: str | None,
            queue_four: str | None,
            queue_five: str | None,
            queue_six: str | None,
            queue_seven: str | None,
            queue_eight: str | None,
            queue_nine: str | None
    ):
        response: InteractionResponse = interaction.response

        queues = [
            queue_one, queue_two, queue_three, queue_four, queue_five,
            queue_six, queue_seven, queue_eight, queue_nine
        ]

        qc_facade = self.bot.managers.guild_state_manager.queue_configs

        result = qc_facade.preview_remove_queues(
            guild_id=interaction.guild.id,
            queues=[q for q in queues if q is not None]
        )

        print(result.to_remove)
        print(result.invalid_queues)

        view = ConfirmRemoveQueuesView(
            interaction=interaction,
            plan=result,
            guild_state_manager=self.bot.managers.guild_state_manager
        )

        await view.dialog()