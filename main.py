import discord
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine

from bot.pickupbot import PickupBot
from config.settings import load_settings
from core.service_context import ServiceContext
from services.guild_registry_service import GuildRegistryService
from services.guild_state_cache import GuildStateCache
from db.engine import get_async_engine
from db.session import init_sessionmaker

def setup_db_session(db_url: str) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    engine = get_async_engine(db_url)
    sessionmaker = init_sessionmaker(engine)
    return engine, sessionmaker

def setup_services(sessionmaker: async_sessionmaker[AsyncSession]) -> ServiceContext:
    return ServiceContext(
        guild_registry_service=GuildRegistryService(sessionmaker=sessionmaker)
    )

def main():
    guild_state_cache = GuildStateCache()

    settings = load_settings()

    # Database
    engine, sessionmaker = setup_db_session(settings.DATABASE_URL)
    service_context = setup_services(sessionmaker)

    intents = discord.Intents.default()
    intents.members = True
    intents.presences = True
    intents.message_content = True

    bot = PickupBot(service_context=service_context,
                    engine=engine,
                    command_prefix="!",
                    intents=intents)

    bot.run(settings.DISCORD_TOKEN)

if __name__ == "__main__":
    main()
