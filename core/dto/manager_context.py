from dataclasses import dataclass

from managers.guild_state_manager import GuildStateManager
from managers.queue_config_manager import QueueConfigManager

@dataclass
class ManagerContext:
    guild_state_manager: GuildStateManager
    queue_config_manager: QueueConfigManager