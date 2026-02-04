from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    DISCORD_TOKEN: str

def load_settings() -> Settings:
    from dotenv import load_dotenv
    load_dotenv()

    token = os.getenv("DISCORD_TOKEN")
    if token is None or len(token) == 0:
        raise RuntimeError('DISCORD_TOKEN not set')

    return Settings(token)