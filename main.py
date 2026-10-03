import asyncio

import app_context
from app_context import AppContext
from config import Config
from database.db import init_db
from messengers.discord.bot import DiscordBot
from messengers.stoat.bot import StoatBot
from services.state import StateService


async def main():

    config: Config = Config()

    # Database
    engine, session_factory = await init_db(config.db_url.get_secret_value())

    bots = []

    state_service = StateService(session_factory)

    context = AppContext(
        state_service=state_service,
    )

    if config.discord_token and config.enable_discord:
        bots.append(DiscordBot(token=config.discord_token.get_secret_value(), app_context=context))

    if config.stoat_token and config.enable_stoat:
        bots.append(StoatBot(token=config.stoat_token.get_secret_value(), app_context=context))

    await asyncio.gather(*(bot.run() for bot in bots))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass