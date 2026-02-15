import asyncio

from core.app_context import setup
from core.dto.guild_info import GuildInfo
from db.init_tables import init_db
from domain.types import GuildId

async def main():
    app_context = setup('sqlite+aiosqlite:///../dev.db')
    state_manager = app_context.manager_context.guild_state_manager
    repo_service = app_context.service_context.guild_repository_service

    await init_db(engine=app_context.engine, gated_command_names=[])

    await state_manager.register_guild(GuildInfo(
        guild_id=GuildId(1467241111402840299),
        name='Test Guild'
    ))

    print(state_manager.get_guild_state(guild_id=GuildId(1467241111402840299)))

if __name__ == "__main__":
    asyncio.run(main())