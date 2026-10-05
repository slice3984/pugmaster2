import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import Config
from database.models import Base

config: Config = Config()

if config.test_db_url is None:
    raise RuntimeError('Please provide a test database URL')

@pytest_asyncio.fixture(scope='session')
async def db_engine():
    if config.test_db_url is None:
        raise RuntimeError('Please provide a test database URL')

    engine = create_async_engine(config.test_db_url.get_secret_value())

    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db(db_engine):
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def session_factory(db_engine):
    return async_sessionmaker(db_engine, expire_on_commit=False)


