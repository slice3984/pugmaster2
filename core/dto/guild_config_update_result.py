from dataclasses import dataclass

from domain.guild_state import GuildSettings


@dataclass
class GuildConfigUpdateResult:
    ok: bool
    settings: GuildSettings | None
    error: str | None