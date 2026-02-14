from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text, insert

from db.base import Base
# Imports needed to register and create the actual tables
from db.models.guild import Guild
from db.models.permission import Permission
from db.models.role_permission import RolePermission
from db.models.guild_role_permission import GuildRolePermission

async def init_tables(engine: AsyncEngine, gated_command_names: Iterable[str]) -> None:
    """Creates tables needed for the database."""
    async with engine.begin() as conn:
        try:
            await conn.execute(text('select 1 from guilds'))
            print('Database initialized, found tables')
        except Exception:
            print('Database not initialized, creating tables')
            await conn.run_sync(Base.metadata.create_all)

            # Insert gated commands names
            insertion_list = [{"permission": name } for name in gated_command_names]

            await conn.execute(
                insert(Permission).values(insertion_list)
            )