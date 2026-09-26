import asyncio

from config import Config
from database.db import init_db
from messengers.discord.bot import DiscordBot
from messengers.stoat.bot import StoatBot


async def main():

    config: Config = Config()

    # Database
    engine, session_factory = await init_db(config.db_url.get_secret_value())

    bots = []

    if config.discord_token and config.enable_discord:
        bots.append(DiscordBot(token=config.discord_token.get_secret_value()))

    if config.stoat_token and config.enable_stoat:
        bots.append(StoatBot(token=config.stoat_token.get_secret_value()))

    for bot in bots:
        await bot.start()

    await asyncio.gather(*(bot.join() for bot in bots))

if __name__ == '__main__':
    asyncio.run(main())

