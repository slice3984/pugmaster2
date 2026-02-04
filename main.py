import discord
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine

from config.settings import load_settings
from bot.cogs.ping import Ping
from services.guild_settings_cache import GuildSettingsCache
from db.engine import get_async_engine
from db.session import init_sessionmaker

from db.init_tables import init_tables

class PickupBot(commands.Bot):
    def __init__(self,
                 *,
                 guild_settings_cache: GuildSettingsCache,
                 engine: AsyncEngine,
                 **kwargs):
        super().__init__(**kwargs)
        self._guild_settings_cache = guild_settings_cache
        self._engine = engine

    async def setup_hook(self) -> None:
        await init_tables(self._engine)
        await self.add_cog(Ping(self))

    async def on_ready(self) -> None:
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def close(self) -> None:
        await super().close()
        await self._engine.dispose()

def setup_db_session(db_url: str) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    engine = get_async_engine(db_url)
    sessionmaker = init_sessionmaker(engine)
    return engine, sessionmaker

def setup_services(sessionmaker: async_sessionmaker[AsyncSession]) -> None:
    pass

def main():
    guild_settings_cache = GuildSettingsCache()

    settings = load_settings()

    # Database
    engine, sessionmaker = setup_db_session(settings.DATABASE_URL)
    setup_services(sessionmaker)

    intents = discord.Intents.default()
    intents.members = True
    intents.presences = True
    intents.message_content = True

    bot = PickupBot(guild_settings_cache=guild_settings_cache, engine=engine, command_prefix="!", intents=intents)
    bot.run(settings.DISCORD_TOKEN)

if __name__ == "__main__":
    main()
