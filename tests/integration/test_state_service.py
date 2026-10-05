import pytest
from dto.messenger import MessengerRegistration
from enums import MessengerType
from services.state import StateService
from services.state.load_community import load_community
from tests.conftest import session_factory


class TestStateService:
    @pytest.fixture
    def state_service(self, db, session_factory):
        return StateService(session_factory=session_factory)

    @pytest.fixture
    def messenger_registration(self):
        return MessengerRegistration(
            messenger_type=MessengerType.DISCORD,
            server_uid='123',
            name='Discord Messenger'
        )

    @pytest.mark.asyncio
    async def test_messenger_registration(
            self,
            state_service,
            messenger_registration,
            session_factory,
    ):
        await state_service.handle_messenger_registration(messenger_registration)

        community_state = state_service.get_community_state(
            messenger_registration.messenger_type,
            messenger_registration.server_uid,
        )

        assert community_state is not None

        community = await load_community(session_factory, messenger_registration)
        assert community is not None

        assert len(community.messengers) == 1
        messenger = community.messengers[0]

        assert messenger.messenger_type == messenger_registration.messenger_type
        assert messenger.server_uid == messenger_registration.server_uid
        assert messenger.name == messenger_registration.name
        assert messenger.prefix == "!"