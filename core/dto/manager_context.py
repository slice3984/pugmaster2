from dataclasses import dataclass

from managers.command_access_manager import CommandAccessManager
from managers.guild_state_manager import GuildStateManager

@dataclass
class ManagerContext:
    guild_state_manager: GuildStateManager
    command_access_manager: CommandAccessManager