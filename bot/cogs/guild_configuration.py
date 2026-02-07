from typing import TYPE_CHECKING

import discord
from discord import app_commands, Interaction, InteractionResponse, Permissions
from discord.ext import commands

from bot.cogs.base_cog import BaseCog
from bot.ui.embeds.guild_setup_embed_factory import GuildSetupEmbedFactory
from domain.guild_state import GuildSettings
from domain.types import GuildId

if TYPE_CHECKING:
    from bot.pickupbot import PickupBot

class GuildConfiguration(BaseCog):
    def __init__(self, bot: PickupBot):
        super().__init__(bot)

    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @app_commands.command(name='setup', description='Setup guild configuration, pickup channel for queues, listen channel for moderation.')
    @app_commands.guild_only()
    async def setup(
            self, interaction: discord.Interaction,
            pickup_channel: discord.TextChannel,
            listen_channel: discord.TextChannel | None,
    ):
        state = self.get_guild_state(GuildId(interaction.guild.id))

        result = await self.bot.service_context.guild_config_service.update_guild_config(GuildSettings(
            guild_id=state.settings.guild_id,
            prefix=state.settings.prefix,
            pickup_channel_id=pickup_channel.id,
            listen_channel_id= listen_channel.id if listen_channel else None,
        ))

        response: InteractionResponse = interaction.response
        await response.send_message(
            embed=GuildSetupEmbedFactory.from_update_result(result),
            ephemeral=True
        )