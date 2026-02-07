from dataclasses import dataclass

from services.guild_config_service import GuildConfigService
from services.guild_registry_service import GuildRegistryService

@dataclass
class ServiceContext:
    guild_registry_service: GuildRegistryService
    guild_config_service: GuildConfigService