from __future__ import annotations
from dataclasses import dataclass, replace

from enums import MessengerType
from type_aliases import ServerUid, ChannelUid

@dataclass(frozen=True)
class MessengerState:
    """Immutable state for a messenger, part of a CommunityState."""

    messenger_type: MessengerType
    server_uid: ServerUid
    prefix: str
    queue_channel_uid: ChannelUid | None = None
    moderation_channel_uid: ChannelUid | None = None

    def update_prefix(self, prefix: str) -> MessengerState:
        return replace(
            self,
            prefix=prefix
        )

    def update_queue_channel(self, queue_channel_uid: ChannelUid) -> MessengerState:
        return replace(
            self,
            queue_channel_uid=queue_channel_uid
        )

    def update_moderation_channel(self, moderation_channel_uid: ChannelUid) -> MessengerState:
        return replace(
            self,
            moderation_channel_uid=moderation_channel_uid
        )