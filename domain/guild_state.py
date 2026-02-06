from dataclasses import dataclass
from typing import Optional, List

from domain.types import GuildId


@dataclass()
class GuildSettings:
    """Stores frequently accessed guild configuration."""
    guild_id: GuildId
    prefix: str
    pickup_channel_id: int | None = None
    listen_channel_id: int | None = None

@dataclass()
class GuildState:
    """Container for cached guild state."""
    settings: GuildSettings
    queue_names: List[str] | None = None
