from domain.guild_state import GuildState
from typing import Dict

class GuildStateCache:
    """Caches retrieved guild settings from the database."""
    def __init__(self) -> None:
        self._guilds: Dict[int, GuildState] = {}

    def __getitem__(self, guild_id: int) -> GuildState | None:
        state = self._guilds.get(guild_id)
        if state is None:
            return None

        return state

    def __setitem__(self, guild_id: int, guild_settings: GuildState) -> None:
        self._guilds[guild_id] = guild_settings

    def __delitem__(self, guild_id: int) -> None:
        del self._guilds[guild_id]

    def update(self, items: Dict[int, GuildState]) -> None:
        for guild_id, guild_settings in items.items():
            self._guilds[guild_id] = guild_settings