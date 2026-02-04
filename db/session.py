from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

def init_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )