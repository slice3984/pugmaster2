from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from dto.messenger import MessengerRegistration
import database.models as orm

async def create_community_messenger(sf: async_sessionmaker[AsyncSession],
                               messenger_registration: MessengerRegistration) -> orm.Community:
    async with sf() as session:
      community = orm.Community()

      messenger = orm.Messenger(
          server_uid=messenger_registration.server_uid,
          name=messenger_registration.name,
          messenger_type=messenger_registration.messenger_type,
      )

      community.messengers.append(messenger)

      session.add(community)
      await session.commit()

      return community