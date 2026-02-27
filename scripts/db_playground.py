import asyncio

from core.app_context import setup
from core.dto.guild_info import GuildInfo
from db.init_tables import init_db
from domain.types import GuildId
from managers.logic.queue_config import QueueCreationData


async def main():
    app_context = setup('sqlite+aiosqlite:///../dev.db')
    state_manager = app_context.manager_context.guild_state_manager
    repo_service = app_context.service_context.guild_repository_service
    queue_service = app_context.service_context.guild_queue_service
    queue_config_manager = app_context.manager_context.queue_config_manager

    await init_db(engine=app_context.engine, gated_command_names=[])

    await state_manager.register_guild(GuildInfo(
        guild_id=GuildId(1467241111402840299),
        name='Test Guild'
    ))

    queues = dict()
    queues['test'] = (10, 2)
    queues['test2'] = (20, 4)

    """
    await queue_service.create_queues(
        guild_id=GuildId(1467241111402840299),
        queues=queues
    )
    """

    db_queues = await queue_service.fetch_queues(guild_id=GuildId(1467241111402840299))
    print(db_queues)

    queue_config_manager.create_queues(GuildId(1467241111402840299), queues=queues)

    res = await state_manager.queue_configs.create_queues(
        guild_id=GuildId(1467241111402840299),
        queues=[
            QueueCreationData(name='test', player_count=30, team_count=3),
            QueueCreationData(name='test2', player_count=30, team_count=3)
        ]
    )

    print(res)

if __name__ == "__main__":
    asyncio.run(main())