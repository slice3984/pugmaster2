import pytest

from domain.community_state import CommunityState
from domain.messenger_state import MessengerState
from enums import MessengerType


class TestCommunityState:
    @pytest.fixture
    def messengers(self):
        return [
            MessengerState(MessengerType.DISCORD, "123", "!"),
            MessengerState(MessengerType.STOAT, "456", "?"),
        ]

    def test_add_messenger_state(self, messengers):
        community = CommunityState(1)

        new_community = community.update_messenger_state(messengers[0])

        assert not community.has_community_state(MessengerType.DISCORD, "123")
        assert new_community.has_community_state(MessengerType.DISCORD, "123")
        assert new_community is not community

    def test_add_second_messenger_state(self, messengers):
        community = CommunityState(1)
        community = community.update_messenger_state(messengers[0])

        new_community = community.update_messenger_state(messengers[1])

        assert new_community.has_community_state(MessengerType.DISCORD, "123")
        assert new_community.has_community_state(MessengerType.STOAT, "456")