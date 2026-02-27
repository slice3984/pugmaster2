from dataclasses import dataclass


@dataclass(frozen=True)
class QueueConfig:
    name: str
    player_count: int
    team_count: int