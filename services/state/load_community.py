from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload

import database.models as orm
from dto.messenger import MessengerRegistration


async def load_community(sf: async_sessionmaker[AsyncSession],
                         messenger_registration: MessengerRegistration) -> orm.Community | None:
    # Obtain the community by using the unique messenger
    async with sf() as session:
        stmt = (
            select(orm.Community)
            .join(orm.Community.messengers)
            .where(
                orm.Messenger.server_uid == messenger_registration.server_uid,
                orm.Messenger.messenger_type == messenger_registration.messenger_type
            )
            .options(selectinload(orm.Community.messengers))
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()