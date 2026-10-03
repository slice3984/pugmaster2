import asyncio
from contextlib import asynccontextmanager
from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from database.models import Messenger
from domain.community_state import CommunityState
from domain.messenger_state import MessengerState
from dto.messenger import MessengerRegistration
from enums import MessengerType
from services.state.create_community_messenger import create_community_messenger
from services.state.load_community import load_community
from type_aliases import CommunityId, ServerUid

import database.models as orm

@dataclass
class StateTransition:
    from_state: CommunityState
    to_state: CommunityState | None = None

class StateService:
    """Manages immutable community state with atomic state transitions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self._community_states: dict[CommunityId, CommunityState] = {}

        # There is no community available at registration, use a temporary lock instead
        self._registration_locks: dict[tuple[MessengerType, ServerUid], asyncio.Lock] = defaultdict(asyncio.Lock)
        self._community_locks: dict[CommunityId, asyncio.Lock] = defaultdict(asyncio.Lock)

    @asynccontextmanager
    async def community(self, community_id: CommunityId):
        async with self._community_locks[community_id]:
            state = self._community_states[community_id]
            state_transition = StateTransition(from_state=state)

            yield state_transition

            if state_transition.to_state is not None:
                self._community_states[community_id] = state_transition.to_state

    async def handle_messenger_registration(self, messenger_registration: MessengerRegistration):
        """
        Handles platform events of joining / loading messenger servers.

        - The call will be ignored in case the messenger is already cached as part of a community.
        - If there is a community this messenger belongs to it will be loaded and cached.
        - If there is no community associated with this messenger a new community and messenger will be created and cached.
        """
        messenger_type, server_uid, name = messenger_registration

        # Already cached, nothing to do
        if self._is_messenger_cached(messenger_type, server_uid):
            return

        # Lock to protect against multiple events triggering registration for the same messenger
        async with self._registration_locks[messenger_type, server_uid]:
            if self._is_messenger_cached(messenger_type, server_uid): return

            is_messenger_stored = await self._is_messenger_persisted(messenger_type, server_uid)

            # There will always be a community which belongs to a messenger, fetch the community and messengers
            if is_messenger_stored:
                community  = await load_community(self._session_factory, messenger_registration)
            else:
                community = await create_community_messenger(self._session_factory, messenger_registration)

            if community:
                community_state = self._construct_community_state(community)
                self._community_states[community.id] = community_state

    def _is_messenger_cached(self, messenger_type: MessengerType, server_uid: ServerUid) -> bool:
        for state in self._community_states.values():
            if state.has_community_state(messenger_type=messenger_type, server_uid=server_uid):
                return True

        return False

    async def _is_messenger_persisted(self, messenger_type: MessengerType, server_uid: ServerUid) -> bool:
        async with self._session_factory() as session:
            stmt = (
                select(orm.Messenger)
                .where(
                    Messenger.server_uid == server_uid,
                    Messenger.messenger_type == messenger_type,
                )
            )
            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

    @staticmethod
    def _construct_community_state(community_orm: orm.Community) -> CommunityState:
        # Messengers
        messengers: dict[MessengerType, MessengerState] = {}

        for messenger in community_orm.messengers:
            messengers[messenger.messenger_type] = MessengerState(
                messenger_type=messenger.messenger_type,
                server_uid=messenger.server_uid,
                prefix=messenger.prefix,
                queue_channel_uid=messenger.queue_channel_uid,
                moderation_channel_uid=messenger.moderation_channel_uid
            )

        # Community state
        return CommunityState(messenger_states=messengers)



