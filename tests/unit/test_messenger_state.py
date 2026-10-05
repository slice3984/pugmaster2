import pytest

from domain.messenger_state import MessengerState
from enums import MessengerType

class TestMessengerState:
    @pytest.fixture
    def state(self):
        return MessengerState(
            messenger_type=MessengerType.DISCORD,
            server_uid="123",
            prefix="!"
        )

    def test_update_prefix(self, state):
        assert state.prefix == '!'
        new_state = state.update_prefix('?')
        assert new_state.prefix == '?'
        assert new_state is not state

    def test_update_channels(self, state):
        assert state.queue_channel_uid is None
        new_state = state.update_queue_channel('123')
        assert new_state.queue_channel_uid == '123'

        assert state.moderation_channel_uid is None
        new_state = state.update_moderation_channel('123')
        assert new_state.moderation_channel_uid == '123'

        assert new_state is not state