from collections.abc import Collection
from enum import Enum, auto

from domain.guild_state import GuildState
from domain.types import RoleId
from managers.logic.permission import has_command_permission


class ChannelScope(Enum):
    GLOBAL = auto()
    PICKUP = auto()
    LISTEN = auto()
    PICKUP_LISTEN = auto()

class PermissionScope(Enum):
    EVERYONE = auto()
    GATED = auto()
    ADMIN = auto()

def check_channel_scope(
        state: GuildState,
        required_scope: ChannelScope,
        current_channel_id: int,
) -> bool:
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
        state: GuildState,
        required_scope: PermissionScope,
        role_ids: Collection[RoleId],
        is_admin: bool,
        command_name: str
) -> bool:
    match required_scope:
        case PermissionScope.EVERYONE:
            return True
        case PermissionScope.GATED:
            return has_command_permission(
                state=state,
                command_name=command_name,
                role_ids=role_ids,
                is_admin=is_admin
            )
        case PermissionScope.ADMIN:
            return is_admin
