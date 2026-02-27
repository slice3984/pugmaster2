from pyexpat.errors import messages
from typing import TYPE_CHECKING

import discord
from discord import app_commands, InteractionResponse
from discord.ext import commands

from bot.cogs.base_cog import BaseCog
from bot.ui.embeds.embed_paginator import EmbedPaginator
from core.dto.embed_paginator_data import EmbedPaginatorData
from domain.types import GuildId, MemberId
from managers.logic.command_access import ChannelScope, PermissionScope

if TYPE_CHECKING:
    from bot.pickupbot import PickupBot

# TODO: Allow additional filtering for future disabled queues; Display if rated

class Queue(BaseCog):
    channel_scope = ChannelScope.PICKUP
    permissions = PermissionScope.EVERYONE

    def __init__(self, bot: PickupBot):
        super().__init__(bot)

    queue = app_commands.Group(
        name='queue',
        description='Queue specific operations'
    )

    async def _queue_list_handler(self,ctx: discord.Interaction | commands.Context):
        # Get queues from cache
        guild_id = ctx.guild_id if isinstance(ctx, discord.Interaction) else ctx.guild.id
        guild_queues = self.bot.managers.guild_state_manager.get_guild_state(GuildId(guild_id)).queues

        queue_names: list[str] = []
        player_counts: list[str] = []

        sorted_queues = sorted(
            guild_queues.values(),
            key=lambda q: (
                -(len(q.player_ids) / q.queue_config.player_count),
                q.queue_config.name.lower()
            )
        )

        for queue in sorted_queues:
            queue_names.append(queue.queue_config.name)
            player_counts.append(f'{len(queue.player_ids)}/{queue.queue_config.player_count}')

        data = EmbedPaginatorData(
            title='Queues',
            data={
                'Name': queue_names,
                'Players': player_counts
            }
        )

        paginator = EmbedPaginator(ctx, data=data)
        await paginator.handle()

    @BaseCog.require_slash()
    @queue.command(name='list', description='List all queues')
    async def queue_list_slash(self, interaction: discord.Interaction):
        await self._queue_list_handler(interaction)

    @commands.command(name='queues', description='List all queues')
    async def queue_list_command(self, ctx: commands.Context):
        await self._queue_list_handler(ctx)