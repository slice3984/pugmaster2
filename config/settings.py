from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    DISCORD_TOKEN: str
    DATABASE_URL: str

def load_settings() -> Settings:
    """Load settings from environment variables."""
    from dotenv import load_dotenv
    load_dotenv()

    token_dt = os.getenv("DISCORD_TOKEN")
    if token_dt is None or len(token_dt) == 0:
        raise RuntimeError('DISCORD_TOKEN not set')

    token_db = os.getenv("DATABASE_URL")
    if token_db is None or len(token_db) == 0:
        raise RuntimeError('DATABASE_URL not set')

    return Settings(token_dt, token_db)