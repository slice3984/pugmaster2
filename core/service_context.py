from dataclasses import dataclass

from services.guild_repository_service import GuildRepositoryService

@dataclass
class ServiceContext:
    guild_repository_service: GuildRepositoryService