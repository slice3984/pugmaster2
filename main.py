import discord
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine

from bot.pickupbot import PickupBot
from config.settings import load_settings
from core.dto.manager_context import ManagerContext
from core.service_context import ServiceContext
from managers.command_access_manager import CommandAccessManager
from managers.guild_state_manager import GuildStateManager
from services.guild_repository_service import GuildRepositoryService
from db.engine import get_async_engine
from db.session import init_sessionmaker

def setup_db_session(db_url: str) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    engine = get_async_engine(db_url)
    sessionmaker = init_sessionmaker(engine)
    return engine, sessionmaker

def setup_services(sessionmaker: async_sessionmaker[AsyncSession]) -> ServiceContext:
    guild_registry_service = GuildRepositoryService(sessionmaker=sessionmaker)

    return ServiceContext(
        guild_repository_service=guild_registry_service,
    )

def setup_managers(service_context: ServiceContext) -> ManagerContext:
    guild_state_manager = GuildStateManager(service_context.guild_repository_service)
    command_access_manager = CommandAccessManager(guild_state_manager=guild_state_manager)

    return ManagerContext(
        guild_state_manager=guild_state_manager,
        command_access_manager=command_access_manager
    )

def main():
    settings = load_settings()

    # Database
    engine, sessionmaker = setup_db_session(settings.DATABASE_URL)
    service_context = setup_services(sessionmaker)
    manager_context = setup_managers(service_context)

    intents = discord.Intents.default()
    intents.members = True
    intents.presences = True
    intents.message_content = True

    bot = PickupBot(manager_context=manager_context,
                    engine=engine,
                    command_prefix="!",
                    intents=intents)

    bot.run(settings.DISCORD_TOKEN)

if __name__ == "__main__":
    main()
