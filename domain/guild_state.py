from dataclasses import dataclass, field
from domain.types import GuildId, RoleId

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
    role_command_permissions: dict[RoleId, set[str]] = field(default_factory=dict)
    queue_names: list[str] | None = None