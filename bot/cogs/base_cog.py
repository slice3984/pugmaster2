from typing import TYPE_CHECKING
import discord
from discord._types import ClientT
from discord.ext import commands
from domain.guild_state import GuildState

if TYPE_CHECKING:
    from bot.pickupbot import PickupBot

class PickupContext(commands.Context):
    guild_state: GuildState | None = None

class BaseCog(commands.Cog):
    """Base class for all cogs."""
    def __init__(self, bot: PickupBot):
        self.bot = bot

    async def get_context(self, origin, /, *, cls=PickupContext):
        return await super().get_context(origin, cls=cls)

    async def cog_before_invoke(self, ctx: PickupContext):
        """Attach the current guild state to the context."""
        if ctx.guild is None:
            ctx.guild_state = None
        else:
            ctx.guild_state = self.bot.service_context.guild_registry_service.get_guild_state(ctx.guild.id)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.guild_id is None:
            return False

        interaction.extras['guild_state'] = self.bot.guild_state_cache[interaction.guild_id]
        return True