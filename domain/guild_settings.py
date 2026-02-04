from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class GuildSettings:
    guild_id: int
    prefix: str
    pickup_channel_id: Optional[int] = None