from enum import Enum, auto
from typing import Iterable

from domain.types import GuildId
from managers.guild_state_manager import GuildStateManager

class ChannelScope(Enum):
    GLOBAL = auto()
    PICKUP = auto()
    LISTEN = auto()
    PICKUP_LISTEN = auto()

class PermissionScope(Enum):
    EVERYONE = auto()
    GATED = auto()
    ADMIN = auto()
    
class CommandAccessManager:
    def __init__(self, guild_state_manager: GuildStateManager) -> None:
        self._guild_state_manager = guild_state_manager

    def check_channel_scope(
            self,
            required_scope: ChannelScope,
            guild_id: GuildId,
            current_channel_id: int,
    ) -> bool:
        state = self._guild_state_manager.get_guild_state(guild_id=guild_id)
        pickup_channel_id = state.settings.pickup_channel_id
        listen_channel_id = state.settings.listen_channel_id

        match required_scope:
            case ChannelScope.GLOBAL:
                return True
            case ChannelScope.PICKUP:
                return pickup_channel_id == current_channel_id
            case ChannelScope.LISTEN:
                return listen_channel_id == current_channel_id
            case ChannelScope.PICKUP_LISTEN:
                return listen_channel_id == current_channel_id or current_channel_id == pickup_channel_id

    def check_permission_scope(
            self,
            required_scope: PermissionScope,
            guild_member_role_ids: Iterable[int],
            is_admin: bool,
            command_name: str
    ) -> bool:
        match required_scope:
            case PermissionScope.EVERYONE:
                return True
            case PermissionScope.GATED:
                if is_admin:
                    return True
                # TODO: Role checks -> RoleManager
                return True
            case PermissionScope.ADMIN:
                return is_admin
