from dataclasses import dataclass, replace
from typing import Collection, Iterable, TYPE_CHECKING

import managers.logic.permission as permission
import managers.logic.command_access as command_access

from domain.types import GuildId, RoleId, ChannelId

if TYPE_CHECKING:
    from managers.guild_state_manager import GuildStateManager

@dataclass(frozen=True)
class AddPermissionUpdateResult:
    added_permissions: frozenset[str]
    new_role_permissions: frozenset[str]

@dataclass(frozen=True)
class RemovePermissionUpdateResult:
    removed_permissions: frozenset[str]
    new_role_permissions: frozenset[str]

class PermissionsFacade:
    def __init__(self, guild_state_manager: GuildStateManager) -> None:
        self._sm: GuildStateManager = guild_state_manager

    async def add_role_permissions(
            self,
            guild_id: GuildId,
            role_id: RoleId,
            command_names: list[str],
            valid_command_names: list[str]
    ) -> AddPermissionUpdateResult:
        """Adds given command execution permissions to a role, updates cache and database."""
        async with self._sm.acquire_lock(guild_id=guild_id):
            state = self._sm._require_state(guild_id=guild_id)

            plan = permission.plan_add_role_permissions(
                state=state,
                role_id=role_id,
                command_names=command_names,
                valid_command_names=valid_command_names
            )

            if plan.to_add:
                await self._sm._repository_service.add_role_permissions(
                    command_names=plan.to_add,
                    guild_id=guild_id,
                    role_id=role_id
                )

                # Update cache
                role_command_permissions = dict(state.role_command_permissions)  # Copy
                role_command_permissions[role_id] = set(plan.new_role_perms)

                self._sm._mutate_state(guild_id, 'role_command_permissions', role_command_permissions)

            return AddPermissionUpdateResult(
                added_permissions=plan.to_add,
                new_role_permissions=plan.new_role_perms,
            )

    async def remove_role_permissions(
            self,
            guild_id: GuildId,
            role_id: RoleId,
            command_names: list[str],
            valid_command_names: list[str]
    ) -> RemovePermissionUpdateResult:
        """Removes given command execution permissions from a role, updates cache and database."""
        async with self._sm.acquire_lock(guild_id=guild_id):
            state = self._sm._require_state(guild_id=guild_id)
            plan = permission.plan_remove_role_permissions(
                state=state,
                role_id=role_id,
                command_names=command_names,
                valid_command_names=valid_command_names
            )

            if plan.to_remove:
                await self._sm._repository_service.remove_role_permissions(
                    command_names=plan.to_remove,
                    guild_id=guild_id,
                    role_id=role_id
                )

                # Cache
                role_command_permissions = dict(state.role_command_permissions)

                if not plan.new_role_perms:
                    role_command_permissions.pop(role_id, None)
                else:
                    role_command_permissions[role_id] = set(plan.new_role_perms)

                self._sm._mutate_state(guild_id, 'role_command_permissions', role_command_permissions)

            return RemovePermissionUpdateResult(
                removed_permissions=plan.to_remove,
                new_role_permissions=plan.new_role_perms,
            )

    async def remove_elevated_roles(
            self,
            guild_id: GuildId,
            role_ids: Collection[RoleId]
    ) -> set[RoleId]:
        """Removes elevated roles, usually used for stale roles."""
        async with self._sm.acquire_lock(guild_id=guild_id):
            state = self._sm._require_state(guild_id=guild_id)

            plan = permission.plan_remove_elevated_roles(state=state, role_ids=role_ids)

            if plan.role_ids:
                await self._sm._repository_service.remove_elevated_roles(
                    guild_id=guild_id,
                    role_ids=plan.role_ids

                )

                role_command_permissions = dict(state.role_command_permissions)

                for role_id in plan.role_ids:
                    role_command_permissions.pop(role_id, None)

                self._sm._mutate_state(guild_id, 'role_command_permissions', role_command_permissions)

            return set(plan.role_ids)

    def has_command_permission(
            self,
            guild_id: GuildId,
            command_name: str,
            role_ids: Iterable[RoleId],
            is_admin: bool
    ):
        """Checks if a user with given roles is allowed to execute given command."""
        state = self._sm._require_state(guild_id=guild_id)

        return permission.has_command_permission(
            state=state,
            command_name=command_name,
            role_ids=role_ids,
            is_admin=is_admin
        )

    def check_channel_scope(
            self,
            guild_id: GuildId,
            required_scope: command_access.ChannelScope,
            current_channel_id: ChannelId
    ) -> bool:
        """Command level check for the correct channel."""
        state = self._sm._require_state(guild_id=guild_id)

        return command_access.check_channel_scope(
            state=state,
            required_scope=required_scope,
            current_channel_id=current_channel_id
        )

    def check_permission_scope(
            self,
            guild_id: GuildId,
            required_scope: command_access.PermissionScope,
            role_ids: Collection[RoleId],
            is_admin: bool,
            command_name: str
    ) -> bool:
        """Performs a permission check against the provided roles and command."""
        state = self._sm._require_state(guild_id=guild_id)

        return command_access.check_permission_scope(
            state=state,
            required_scope=required_scope,
            role_ids=role_ids,
            is_admin=is_admin,
            command_name=command_name
        )