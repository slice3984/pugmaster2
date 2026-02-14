from dataclasses import dataclass

from domain.types import RoleId

@dataclass(frozen=True)
class GuildRolePermissionResult:
    role_id: RoleId
    allowed_commands: list[str]