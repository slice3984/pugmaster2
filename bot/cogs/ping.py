from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord import app_commands

from bot.cogs.base_cog import BaseCog, PickupContext

if TYPE_CHECKING:
    from bot.pickupbot import PickupBot

class Ping(BaseCog):
    def __init__(self, bot: PickupBot):
        super().__init__(bot)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        print(message.content)

    """
    @commands.command(name='ping')
    async def ping_prefix(self, ctx):
        await ctx.send('pong') @ app_commands.command(name='ping', description='Ping the bot')

    async def ping_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message('pong')

    """

    @commands.hybrid_command(name='ping', description='Ping the bot')
    @app_commands.guild_only()
    async def ping(self, ctx: PickupContext, mode: str | None = None):
        print(ctx.guild_state)

        mode = (mode or 'normal').lower()

        if mode in ('normal', 'n'):
            await ctx.reply('pong', mention_author=False)
        elif mode in ('loud', 'lo'):
            await ctx.reply('PONG!', mention_author=False)
        elif mode in ('latency', 'lat', 'ms'):
            ms = round(ctx.bot.latency * 1000)
            await ctx.reply(f"pong ({ms} ms)", mention_author=False)
        else:
            await ctx.reply(
                f'Unknown mode `{mode}`. Try: normal, loud, latency.',
                mention_author=False,
            )

    @ping.autocomplete('mode')
    async def ping_mode_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str,
    ):
        options = [
            ('normal', 'normal'),
            ('loud', 'loud'),
            ('latency (ms)', 'latency'),
        ]

        current_l = (current or '').lower()
        matches = [
            app_commands.Choice(name=name, value=value)
            for name, value in options
            if current_l in name.lower() or current_l in value.lower()
        ]

        return matches[:25]
