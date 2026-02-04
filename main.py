import discord
from discord.ext import commands

from config.settings import load_settings
from bot.cogs.ping import Ping
from services.guild_settings_cache import GuildSettingsCache
from domain.guild_settings import GuildSettings

class PickupBot(commands.Bot):
    def __init__(self, *, guild_settings_cache: GuildSettingsCache, **kwargs):
        super().__init__(**kwargs)
        self._guild_settings_cache = guild_settings_cache

    async def setup_hook(self) -> None:
        await self.add_cog(Ping(self))

    async def on_ready(self) -> None:
        print(f'Logged in as {self.user} (ID: {self.user.id})')

def main():
    guild_settings_cache = GuildSettingsCache()


    settings = load_settings()

    intents = discord.Intents.default()
    intents.members = True
    intents.presences = True
    intents.message_content = True

    bot = PickupBot(guild_settings_cache=guild_settings_cache, command_prefix="!", intents=intents)
    bot.run(settings.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
