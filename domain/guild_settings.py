from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class GuildSettings:
    """Container for cached guild settings."""
    guild_id: int
    prefix: str
    pickup_channel_id: Optional[int] = None