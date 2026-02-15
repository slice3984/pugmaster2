from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine

from core.dto.manager_context import ManagerContext
from core.service_context import ServiceContext
from db.engine import get_async_engine
from db.session import init_sessionmaker
from managers.command_access_manager import CommandAccessManager
from managers.guild_state_manager import GuildStateManager
from services.guild_repository_service import GuildRepositoryService

@dataclass(frozen=True)
class AppContext:
    engine: AsyncEngine
    service_context: ServiceContext
    manager_context: ManagerContext

def setup(db_url: str) -> AppContext:
    # DB
    engine = get_async_engine(db_url)
    sessionmaker = init_sessionmaker(engine)

    # Services
    guild_repository_service = GuildRepositoryService(sessionmaker=sessionmaker)

    # Managers
    guild_state_manager = GuildStateManager(guild_repository_service)
    command_access_manager= CommandAccessManager(guild_state_manager)

    return AppContext(
        engine=engine,
        service_context=ServiceContext(
            guild_repository_service=guild_repository_service,
        ),
        manager_context=ManagerContext(
            command_access_manager=command_access_manager,
            guild_state_manager=guild_state_manager,
        )
    )


