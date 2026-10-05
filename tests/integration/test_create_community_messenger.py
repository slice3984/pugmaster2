import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import database.models as orm
from dto.messenger import MessengerRegistration
from enums import MessengerType
from services.state.create_community_messenger import create_community_messenger


@pytest.mark.asyncio
async def test_create_community_messenger(db, session_factory):
    messenger_registration = MessengerRegistration(
        messenger_type=MessengerType.DISCORD,
        server_uid='123',
        name='Discord Messenger'
    )

    await create_community_messenger(session_factory, messenger_registration)

    async with session_factory() as session:
        stmt = (
            select(orm.Community)
            .join(orm.Community.messengers)
            .where(
                orm.Messenger.server_uid == messenger_registration.server_uid,
                orm.Messenger.messenger_type == messenger_registration.messenger_type
            )
            .options(selectinload(orm.Community.messengers))
        )

        community_orm = (await session.execute(stmt)).scalar_one_or_none()

    assert community_orm is not None
    messenger_orm = community_orm.messengers[0]
    assert messenger_orm.messenger_type == messenger_registration.messenger_type
    assert messenger_orm.server_uid == messenger_registration.server_uid
    assert messenger_orm.name == messenger_registration.name
    assert messenger_orm.prefix == '!'