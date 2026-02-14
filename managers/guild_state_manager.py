import asyncio
from dataclasses import replace
from typing import Iterable

from core.dto.guild_config_update_result import GuildConfigUpdateResult
from core.dto.guild_info import GuildInfo
from domain.guild_state import GuildState, GuildSettings
from domain.types import GuildId, RoleId
from services.guild_repository_service import GuildRepositoryService, GuildNotCachedError
from services.guild_state_cache import GuildStateCache


class GuildStateManager:
    def __init__(self, guild_repository_service: GuildRepositoryService) -> None:
        self._cache = GuildStateCache()
        self._repository_service = guild_repository_service
        self._locks: dict[GuildId, asyncio.Lock] = {}

    def _require_state(self, guild_id: GuildId) -> GuildState:
        state = self._cache[guild_id]

        if state is None:
            raise GuildNotCachedError(f'Guild {guild_id} not cached')

        return state

    async def register_guild(self, guild: GuildInfo) -> None:
        """Loads and caches guild state if necessary."""
        # Only register if not in cache
        if self._cache[guild.guild_id] is not None:
            return

        lock = self._locks.setdefault(guild.guild_id, asyncio.Lock())

        async with lock:
            if self._cache[guild.guild_id] is not None:
                return

            guild_settings = await self._repository_service.fetch_guild_settings(guild_info=guild)
            guild_role_permissions = await self._repository_service.fetch_guild_role_permissions(
                guild_id=guild.guild_id)

            self._cache[guild.guild_id] = GuildState(
                settings=guild_settings,
                role_command_permissions=guild_role_permissions
            )

    async def register_guilds(self, guilds: Iterable[GuildInfo]) -> None:
        for guild in guilds:
            await self.register_guild(guild)

    async def update_guild_config(self, guild_settings: GuildSettings) -> GuildConfigUpdateResult:
        """Updates guild settings in database and cache."""
        state = self._require_state(guild_settings.guild_id)

        if guild_settings.listen_channel_id == guild_settings.pickup_channel_id:
            return GuildConfigUpdateResult(
                ok=False,
                settings=None,
                error='Pickup and Listen channel should differ from each other.'
            )

        lock = self._locks.setdefault(guild_settings.guild_id, asyncio.Lock())
        async with lock:
            state = self._require_state(guild_settings.guild_id)
            updated = await self._repository_service.update_guild_settings(guild_settings=guild_settings)

            if not updated:
                return GuildConfigUpdateResult(
                    ok=False,
                    settings=None,
                    error='Something went wrong updating the database.'
                )

            new_settings = replace(
                state.settings,
                pickup_channel_id=guild_settings.pickup_channel_id,
                listen_channel_id=guild_settings.listen_channel_id
            )

            new_state = replace(state, settings=new_settings)
            self._cache[guild_settings.guild_id] = new_state

            return GuildConfigUpdateResult(ok=True, settings=new_settings, error=None)

    def get_guild_state(self, guild_id: GuildId) -> GuildState:
        return self._require_state(guild_id)

    async def evict_guild_state(self, guild_id: GuildId) -> None:
        lock = self._locks.setdefault(guild_id, asyncio.Lock())
        async with lock:
            if self._cache[guild_id] is not None:
                del self._cache[guild_id]

    def _filter_role_permissions(
            self,
            intersection: bool,
            guild_id: GuildId,
            role_id: RoleId,
            command_names: list[str],
            valid_command_names: list[str]
    ) -> list[str]:
        """Checks given commands for validity and performs a difference or intersection check against the given role_id."""
        state = self._require_state(guild_id)

        # Validate command names
        command_names = [command for command in command_names if command in valid_command_names]

        if not command_names:
            return []

        role_associated_permissions: set[str] = set()

        if role_id in state.role_command_permissions:
            role_associated_permissions = state.role_command_permissions[role_id]

        if intersection:
            left_permissions = list(set(command_names) & role_associated_permissions)
        else:
            left_permissions = list(set(command_names) - role_associated_permissions)

        return left_permissions

    async def add_role_permissions(
            self,
            guild_id: GuildId,
            role_id: RoleId,
            command_names: list[str],
            valid_command_names: list[str]
    ) -> list[str]:
        """Adds permissions to a guild role, returns a list of actually added permissions."""
        # First check before reaching the lock, if the returned list is empty, there are no permissions to add
        if not self._filter_role_permissions(intersection=False,
                                             guild_id=guild_id,
                                             role_id=role_id,
                                             command_names=command_names,
                                             valid_command_names=valid_command_names
                                             ):
            return []

        lock = self._locks.setdefault(guild_id, asyncio.Lock())
        async with lock:
            # Recheck cache
            command_names = self._filter_role_permissions(intersection=False,
                                                          guild_id=guild_id,
                                                          role_id=role_id,
                                                          command_names=command_names,
                                                          valid_command_names=valid_command_names
                                                          )

            if not command_names:
                return []

            await self._repository_service.add_role_permissions(command_names=command_names, guild_id=guild_id,
                                                                role_id=role_id)

            # Update cache
            state = self._require_state(guild_id)
            role_command_permissions = dict(state.role_command_permissions) # Copy

            if role_id not in state.role_command_permissions:
                role_command_permissions[role_id] = set(command_names)
            else:
                role_command_permissions[role_id].update(command_names)

            new_state = replace(state, role_command_permissions=role_command_permissions)
            self._cache[guild_id] = new_state
            return command_names

    async def remove_role_permissions(
            self,
            guild_id: GuildId,
            role_id: RoleId,
            command_names: list[str],
            valid_command_names: list[str]
    ) -> list[str]:
        """Removes permissions from a guild role, returns a list of actually removed permissions."""
        if not self._filter_role_permissions(
                intersection=True,
                guild_id=guild_id,
                role_id=role_id,
                command_names=command_names,
                valid_command_names=valid_command_names
        ):
            return []

        lock = self._locks.setdefault(guild_id, asyncio.Lock())
        async with lock:
            command_names = self._filter_role_permissions(
                intersection=True,
                guild_id=guild_id,
                role_id=role_id,
                command_names=command_names,
                valid_command_names=valid_command_names
            )

            if not command_names:
                return []

            await self._repository_service.remove_role_permissions(
                guild_id=guild_id,
                command_names=command_names,
                role_id=role_id
            )

            # Update cache
            state = self._require_state(guild_id)
            role_command_permissions = dict(state.role_command_permissions)
            current_role_permissions = role_command_permissions[role_id]

            role_command_permissions[role_id] = set([c for c in current_role_permissions if c not in command_names])
            new_state = replace(state, role_command_permissions=role_command_permissions)
            self._cache[guild_id] = new_state

            return command_names

    def _filter_roles_present_in_cache(
            self,
            guild_id: GuildId,
            role_ids: list[RoleId]
    ) -> list[RoleId]:
        state = self._require_state(guild_id)
        valid_role_ids: list[RoleId] = []

        for role_id in role_ids:
            if role_id in state.role_command_permissions:
                valid_role_ids.append(role_id)

        return valid_role_ids

    async def remove_elevated_roles(self, guild_id: GuildId, role_ids: list[RoleId]):
        """Removes elevated roles from cache and database, usually used to remove stale roles."""
        # Cache check
        if not self._filter_roles_present_in_cache(guild_id, role_ids):
            return

        lock = self._locks.setdefault(guild_id, asyncio.Lock())
        async with lock:
            valid_role_ids = self._filter_roles_present_in_cache(guild_id, role_ids)

            if not valid_role_ids:
                return

            await self._repository_service.remove_elevated_roles(guild_id, valid_role_ids)
            state = self._require_state(guild_id)
            role_command_permissions = dict(state.role_command_permissions)

            for role_id in valid_role_ids:
                role_command_permissions.pop(role_id, None)

            new_state = replace(state, role_command_permissions=role_command_permissions)
            self._cache[guild_id] = new_state