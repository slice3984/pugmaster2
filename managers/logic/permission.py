from dataclasses import dataclass
from typing import Collection, Iterable

from domain.guild_state import GuildState
from domain.types import RoleId, GuildId

@dataclass(frozen=True)
class AddRolePermissionPlan:
    guild_id: GuildId
    role_id: RoleId
    to_add: frozenset[str]
    new_role_perms: frozenset[str]

def _filter_role_permissions(
        state: GuildState,
        intersection: bool,
        role_id: RoleId,
        command_names: list[str],
        valid_command_names: list[str]
) -> set[str]:
    """Checks given commands for validity and performs a difference or intersection check against the given role_id."""
    # Validate command names
    command_names = [command for command in command_names if command in valid_command_names]

    if not command_names:
        return set()

    role_associated_permissions: set[str] = set()

    if role_id in state.role_command_permissions:
        role_associated_permissions = state.role_command_permissions[role_id]

    if intersection:
        left_permissions = list(set(command_names) & role_associated_permissions)
    else:
        left_permissions = list(set(command_names) - role_associated_permissions)

    return set(left_permissions)


def plan_add_role_permissions(
        state: GuildState,
        role_id: RoleId,
        command_names: list[str],
        valid_command_names: list[str],
) -> AddRolePermissionPlan:
    command_names_to_add = _filter_role_permissions(
        state=state,
        intersection=False,
        role_id=role_id,
        command_names=command_names,
        valid_command_names=valid_command_names
    )

    role_permissions = set(state.role_command_permissions.get(role_id, set()))
    new_role_perms = frozenset(role_permissions | command_names_to_add)

    return AddRolePermissionPlan(
        guild_id=state.settings.guild_id,
        role_id=role_id,
        to_add=frozenset(command_names_to_add),
        new_role_perms=new_role_perms,
    )

@dataclass(frozen=True)
class RemoveRolePermissionPlan:
    guild_id: GuildId
    role_id: RoleId
    to_remove: frozenset[str]
    new_role_perms: frozenset[str]

def plan_remove_role_permissions(
        state: GuildState,
        role_id: RoleId,
        command_names: list[str],
        valid_command_names: list[str],
) -> RemoveRolePermissionPlan:
    command_names_to_remove = _filter_role_permissions(
        state=state,
        intersection=True,
        role_id=role_id,
        command_names=command_names,
        valid_command_names=valid_command_names,
    )

    role_permissions = set(state.role_command_permissions.get(role_id, set()))
    new_role_perms = frozenset(role_permissions - command_names_to_remove)

    return RemoveRolePermissionPlan(
        guild_id=state.settings.guild_id,
        role_id=role_id,
        to_remove=frozenset(command_names_to_remove),
        new_role_perms=new_role_perms,
    )

def _filter_roles_present_in_cache(
        state: GuildState,
        role_ids: Collection[RoleId]
) -> frozenset[RoleId]:
    valid_role_ids: list[RoleId] = []

    for role_id in role_ids:
        if role_id in state.role_command_permissions:
            valid_role_ids.append(role_id)

    return frozenset(valid_role_ids)

@dataclass(frozen=True)
class RemoveElevatedRolePermissionPlan:
    guild_id: GuildId
    role_ids: frozenset[RoleId]

def plan_remove_elevated_roles(
        state: GuildState,
        role_ids: Collection[RoleId]
) -> RemoveElevatedRolePermissionPlan:
    return RemoveElevatedRolePermissionPlan(
        guild_id=state.settings.guild_id,
        role_ids=_filter_roles_present_in_cache(state=state, role_ids=role_ids)
    )

def has_command_permission(
        state: GuildState,
        command_name: str,
        role_ids: Iterable[RoleId],
        is_admin: bool
):
    """Check if a certain user has command execution permission."""
    if is_admin:
        return True

    elevated_roles = state.role_command_permissions

    for role_id in role_ids:
        perms = elevated_roles.get(role_id)

        if perms and command_name in perms:
            return True

    return False
