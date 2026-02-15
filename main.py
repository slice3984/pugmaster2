import discord
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine

from bot.pickupbot import PickupBot
from config.settings import load_settings
from core.app_context import setup
def main():
    settings = load_settings()
    app_context = setup(settings.DATABASE_URL)

    intents = discord.Intents.default()
    intents.members = True
    intents.presences = True
    intents.message_content = True

    bot = PickupBot(manager_context=app_context.manager_context,
                    engine=app_context.engine,
                    command_prefix="!",
                    intents=intents)

    bot.run(settings.DISCORD_TOKEN)

if __name__ == "__main__":
    main()
