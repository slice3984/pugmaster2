from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

def get_async_engine(url: str) -> AsyncEngine:
    return create_async_engine(url)