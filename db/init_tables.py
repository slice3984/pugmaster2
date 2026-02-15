from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import insert

from db.base import Base
import db.models
from db.models.permission import Permission


async def init_schema(engine: AsyncEngine) -> None:
    """Create missing tables or the entire database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_permissions(engine: AsyncEngine, gated_command_names: Iterable[str]) -> None:
    """Insert gated command names if missing."""
    values = [{"permission": name} for name in gated_command_names]

    if not values:
        return

    stmt = insert(Permission).values(values)
    stmt = stmt.prefix_with("OR IGNORE")

    async with engine.begin() as conn:
        await conn.execute(stmt)


async def init_db(engine: AsyncEngine, gated_command_names: Iterable[str]) -> None:
    await init_schema(engine)
    await seed_permissions(engine, gated_command_names)