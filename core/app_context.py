from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine

from core.dto.manager_context import ManagerContext
from core.service_context import ServiceContext
from db.engine import get_async_engine
from db.session import init_sessionmaker
from managers.guild_state_manager import GuildStateManager
from managers.queue_config_manager import QueueConfigManager
from services.guild_queue_service import GuildQueueService
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
    guild_queue_service = GuildQueueService(sessionmaker=sessionmaker)

    # Managers
    guild_state_manager = GuildStateManager(guild_repository_service, guild_queue_service)
    queue_config_manager = QueueConfigManager(guild_queue_service, guild_state_manager)

    return AppContext(
        engine=engine,
        service_context=ServiceContext(
            guild_repository_service=guild_repository_service,
            guild_queue_service=guild_queue_service,
        ),
        manager_context=ManagerContext(
            guild_state_manager=guild_state_manager,
            queue_config_manager=queue_config_manager,
        )
    )


