from dataclasses import dataclass

from domain.types import GuildId


@dataclass(frozen=True)
class GuildInfo:
    guild_id: GuildId
    name: str