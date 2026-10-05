from __future__ import annotations
from dataclasses import dataclass, field, replace

from domain.messenger_state import MessengerState
from enums import MessengerType
from type_aliases import ServerUid, CommunityId


@dataclass(frozen=True)
class CommunityState:
    """Immutable state for a community, interconnects the state of multiple messengers."""

    # ID of the community in the database
    community_id: CommunityId
    messenger_states: dict[MessengerType, MessengerState] = field(default_factory=dict)
    # ...

    def update_messenger_state(self, messenger_state: MessengerState) -> CommunityState:
        return replace(
            self,
            messenger_states = self.messenger_states | {
                messenger_state.messenger_type: messenger_state
            }
        )

    def has_community_state(self, messenger_type: MessengerType, server_uid: ServerUid | None = None) -> bool:
        if not messenger_type in self.messenger_states:
            return False

        state = self.messenger_states[messenger_type]

        return state.server_uid == server_uid