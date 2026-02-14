from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

def get_async_engine(url: str) -> AsyncEngine:
    engine = create_async_engine(url)

    # for SQLite on delete cascade
    if url.startswith("sqlite"):
        @event.listens_for(engine.sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine