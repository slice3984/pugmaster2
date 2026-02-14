import asyncio
from typing import cast

from sqlalchemy import update, CursorResult, select, delete
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from core.dto.guild_info import GuildInfo
from db.models.guild import Guild
from db.models.guild_role_permission import GuildRolePermission
from db.models.role_permission import RolePermission
from domain.guild_state import GuildSettings
from domain.types import GuildId, RoleId
from services.guild_state_cache import GuildStateCache

class GuildNotCachedError(RuntimeError):
    pass

class GuildRepositoryService:
    """Updates, deletes and creates guild state, communicates with the database."""

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sessionmaker = sessionmaker
        self._locks: dict[int, asyncio.Lock] = {}
        self._guild_state_cache: GuildStateCache = GuildStateCache()

    async def fetch_guild_settings(self, guild_info: GuildInfo) -> GuildSettings:
        async with self._sessionmaker() as session:
            async with session.begin():
                db_guild = await session.get(Guild, guild_info.guild_id)

                if db_guild is None:
                    db_guild = Guild(guild_id=guild_info.guild_id, name=guild_info.name, prefix='!')
                    session.add(db_guild)

                return GuildSettings(
                    guild_id = guild_info.guild_id,
                    prefix=db_guild.prefix,
                    listen_channel_id=db_guild.listen_channel_id,
                    pickup_channel_id=db_guild.pickup_channel_id
                )

    async def update_guild_settings(self, guild_settings: GuildSettings) -> bool:
        async with self._sessionmaker() as session:
            async with session.begin():
                stmt = (
                    update(Guild)
                    .where(Guild.guild_id == guild_settings.guild_id)
                    .values(
                        pickup_channel_id=guild_settings.pickup_channel_id,
                        listen_channel_id=guild_settings.listen_channel_id
                    )
                )

                result: Result = await session.execute(stmt)
                cursor_result = cast(CursorResult, result)

                # In case the dbms did not update any data, should not happen
                if cursor_result.rowcount == 0:
                    return False

        return True

    async def add_role_permissions(
            self,
            command_names: list[str],
            guild_id: GuildId,
            role_id: RoleId
    ):
        """Adds permissions to a guild role on database level."""
        async with self._sessionmaker() as session:
            try:
                async with session.begin():
                    role = await session.get(GuildRolePermission, (guild_id, role_id))

                    if role is None:
                        role = GuildRolePermission(guild_id=guild_id, role_id=role_id)
                        session.add(role)

                    for command in command_names:
                        session.add(RolePermission(
                            guild_id=guild_id,
                            role_id=role_id,
                            permission_key=command
                        ))
            except IntegrityError:
                # Not supposed to happen, TODO: Log it
                pass

    async def remove_role_permissions(self, command_names: list[str], guild_id: GuildId, role_id: RoleId) -> list[str]:
        """Removes permissions from a guild role on database level."""
        removed_permissions: list[str] = []

        async with self._sessionmaker() as session:
            async with session.begin():
                stmt = select(RolePermission).where(
                    RolePermission.guild_id == guild_id,
                    RolePermission.role_id == role_id,
                    RolePermission.permission_key.in_(command_names)
                )

                role_permissions = (await session.execute(stmt)).scalars().all()

                for role_permission in role_permissions:
                    removed_permissions.append(role_permission.permission_key)
                    await session.delete(role_permission)

        return removed_permissions

    async def fetch_guild_role_permissions(self, guild_id: GuildId) -> dict[RoleId, set[str]]:
        """Fetches all elevated roles for a guild, used for caching."""
        async with self._sessionmaker() as session:
            async with session.begin():
                stmt = select(RolePermission).where(
                    RolePermission.guild_id == guild_id
                )

                fetched_roles: dict[RoleId, set[str]] = {}
                role_permissions: list[RolePermission] = (await session.execute(stmt)).scalars().all()

                for role_permission in role_permissions:
                    fetched_roles.setdefault(RoleId(role_permission.role_id), set()).add(role_permission.permission_key)

                return fetched_roles

    async def remove_elevated_roles(self, guild_id: GuildId, role_ids: list[RoleId]) -> None:
        """Removes elevated roles for a guild, usually used for stale roles."""
        if not role_ids:
            return

        async with self._sessionmaker() as session:
            async with session.begin():
                await session.execute(
                    delete(GuildRolePermission)
                    .where(
                        GuildRolePermission.guild_id == guild_id,
                        GuildRolePermission.role_id.in_(role_ids)
                    )
                )