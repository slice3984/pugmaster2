from datetime import datetime
from dataclasses import dataclass, field
from typing import TypeAlias, Literal

from core.dto.queue_config import QueueConfig
from domain.types import GuildId, RoleId, MemberId

GuildStateField: TypeAlias = Literal[
    'settings',
    'role_command_permissions',
    'queues',
]

ActiveGuildPrompt: TypeAlias = Literal[
    'QueueRemovalPrompt'
]

@dataclass()
class GuildSettings:
    """Stores frequently accessed guild configuration."""
    guild_id: GuildId
    prefix: str
    pickup_channel_id: int | None = None
    listen_channel_id: int | None = None

@dataclass()
class QueueState:
    """Stores queues of a guild including their state."""
    queue_config: QueueConfig
    player_ids: set[MemberId] = field(default_factory=set)

@dataclass()
class GuildState:
    """Container for cached guild state."""
    settings: GuildSettings
    role_command_permissions: dict[RoleId, set[str]] = field(default_factory=dict)
    queues: dict[str, QueueState] = field(default_factory=dict) # Key: Queue name Value: State
    active_prompts: dict[ActiveGuildPrompt, datetime] = field(default_factory=dict) # Key: Prompt Value: created at time