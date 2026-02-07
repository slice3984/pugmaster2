from typing import TYPE_CHECKING
import discord
from discord._types import ClientT
from discord.ext import commands
from domain.guild_state import GuildState
from domain.types import GuildId
from services.guild_registry_service import GuildNotCachedError

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

    def get_guild_state(self, guild_id: GuildId) -> GuildState:
        state = self.bot.service_context.guild_registry_service.get_guild_state(GuildId(guild_id))

        if state is None:
            raise GuildNotCachedError(guild_id)

        return state