import pytest

import database.models as orm
from dto.messenger import MessengerRegistration
from enums import MessengerType
from services.state.load_community import load_community


@pytest.mark.asyncio
async def test_load_community(db, session_factory):
    # Create a demo community first
    messenger_registration = MessengerRegistration(
        messenger_type=MessengerType.DISCORD,
        server_uid='123',
        name='Discord Messenger'
    )

    async with session_factory() as session:
        community = orm.Community()

        messenger = orm.Messenger(
            messenger_type=messenger_registration.messenger_type,
            server_uid=messenger_registration.server_uid,
            name=messenger_registration.name,
        )

        community.messengers.append(messenger)
        session.add(community)
        await session.commit()

    # Load and test
    community_orm = await load_community(session_factory, messenger_registration)
    assert community_orm is not None
    assert community_orm.id == community.id

    messenger_orm = community_orm.messengers[0]
    assert messenger_orm.messenger_type == MessengerType.DISCORD
    assert messenger_orm.server_uid == messenger_registration.server_uid
    assert messenger_orm.name == messenger_registration.name
    assert messenger_orm.prefix == '!'