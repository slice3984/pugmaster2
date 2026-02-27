import re
from dataclasses import dataclass
from typing import Iterable, Collection

from core.dto.queue_config import QueueConfig
from domain.guild_state import GuildState, QueueState
from domain.queue_constants import MIN_QUEUE_NAME_LENGTH, MAX_QUEUE_NAME_LENGTH, MAX_PLAYER_COUNT, MIN_PLAYER_COUNT, \
    MIN_TEAM_COUNT, MAX_TEAM_COUNT, MAX_GUILD_QUEUE_COUNT
from domain.types import GuildId

def _filter_queue_names(
        state: GuildState,
        intersection: bool,
        queue_names: Iterable[str]
) -> list[str]:
    if intersection:
        return [queue for queue in queue_names if queue in state.queues.keys()]
    else:
        return [queue for queue in queue_names if queue not in state.queues.keys()]

def _validate_queue_data_like(
        data: QueueCreationData | QueueConfig
) -> list[str]:
    """Validate queue config like data, returns a list of possible errors."""
    errors: list[str] = []

    # Common in QueueCreationData and QueueConfig
    if not re.compile(r"^[\w\-]+$", re.UNICODE).fullmatch(data.name):
        errors.append(f'Queue name may contain only letters, numbers, underscores (_) and hyphens (-)')

    if not (MIN_QUEUE_NAME_LENGTH <= len(data.name) <= MAX_QUEUE_NAME_LENGTH):
        errors.append(f'Queue name length must be between {MIN_QUEUE_NAME_LENGTH} and {MAX_QUEUE_NAME_LENGTH}')

    if not (MIN_PLAYER_COUNT <= data.player_count <= MAX_PLAYER_COUNT):
        errors.append(f'Player count must be between {MIN_PLAYER_COUNT} and {MAX_PLAYER_COUNT}')

    if not (MIN_TEAM_COUNT <= data.team_count <= MAX_TEAM_COUNT):
        errors.append(f'Team count must be between {MIN_TEAM_COUNT} and {MAX_TEAM_COUNT}')

    if not data.player_count % data.team_count == 0:
        errors.append('Player count must be evenly divisible by team count')

    if isinstance(data, QueueCreationData):
        return errors

    # QueueConfig extras
    # ...
    return errors

@dataclass(frozen=True)
class CreateQueuesPlan:
    guild_id: GuildId
    to_add: frozenset[QueueCreationData]
    errors: dict[str, list[str]]

@dataclass(frozen=True)
class QueueCreationData:
    name: str
    player_count: int
    team_count: int

def plan_create_queues(
    state: GuildState,
    queues: Collection[QueueCreationData]
) -> CreateQueuesPlan:
    errors: dict[str, list[str]] = {}

    # Deduping, lowercase
    seen = set()
    sanitized_queues: list[QueueCreationData] = []

    for q in queues:
        name = q.name.lower()
        if name not in seen:
            seen.add(name)
            sanitized_queues.append(QueueCreationData(
                name=name,
                player_count=q.player_count,
                team_count=q.team_count,
            ))

    # Check if already stored
    valid_queue_names = _filter_queue_names(
        state=state,
        intersection=False,
        queue_names=seen,
    )

    already_stored = seen - set(valid_queue_names)

    for already_stored_queue in already_stored:
        errors.setdefault(already_stored_queue, []).append('Already stored')

    # Parameter validation
    pre_validated_queues = [queue for queue in sanitized_queues if queue.name in valid_queue_names]

    valid_queues: list[QueueCreationData] = []

    for queue in pre_validated_queues:
        validation_errors = _validate_queue_data_like(queue)

        if validation_errors:
            errors.setdefault(queue.name, []).extend(validation_errors)
        else:
            valid_queues.append(queue)

    # Check if total queue limit is reached
    if len(state.queues) + len(valid_queues) > MAX_GUILD_QUEUE_COUNT:
        # TODO: Actually take disabled queues into account
        return CreateQueuesPlan(
            guild_id=state.settings.guild_id,
            to_add=frozenset(),
            errors={q.name: [f'Exceeded total queue amount of {MAX_GUILD_QUEUE_COUNT}'] for q in valid_queues}
        )

    return CreateQueuesPlan(
        guild_id=state.settings.guild_id,
        to_add=frozenset(valid_queues),
        errors=errors,
    )

@dataclass(frozen=True)
class RemoveQueuesPlan:
    guild_id: GuildId
    to_remove: frozenset[str]
    invalid_queues: frozenset[str]

def plan_remove_queues(
        state: GuildState,
        queue_names: Iterable[str]
) -> RemoveQueuesPlan:
    valid_queue_names = _filter_queue_names(state=state, queue_names=queue_names, intersection=True)
    invalid_queue_names = set(queue_names) - set(valid_queue_names)

    return RemoveQueuesPlan(
        guild_id=state.settings.guild_id,
        to_remove=frozenset(valid_queue_names),
        invalid_queues=frozenset(invalid_queue_names)
    )