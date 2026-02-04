from domain.guild_settings import GuildSettings
from typing import Dict

class GuildSettingsCache:
    """Caches retrieved guild settings from the database."""
    def __init__(self) -> None:
        self._guilds: Dict[int, GuildSettings] = {}

    def __getitem__(self, guild_id: int) -> GuildSettings:
        return self._guilds[guild_id]

    def __setitem__(self, guild_id: int, guild_settings: GuildSettings) -> None:
        self._guilds[guild_id] = guild_settings

    def update(self, items: Dict[int, GuildSettings]) -> None:
        for guild_id, guild_settings in items.items():
            self._guilds[guild_id] = guild_settings