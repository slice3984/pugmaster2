from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text

from db.base import Base
from db.models.guild import Guild

async def init_tables(engine: AsyncEngine) -> None:
    """Creates tables needed for the database."""
    async with engine.begin() as conn:
        try:
            await conn.execute(text('select 1 from guilds'))
            print('Database initialized, found tables')
        except Exception:
            print('Database not initialized, creating tables')
            await conn.run_sync(Base.metadata.create_all)