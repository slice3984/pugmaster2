import hikari

from app_context import AppContext
from messengers.discord.events import DiscordEvents


class DiscordBot:
    def __init__(self, token: str, app_context: AppContext) -> None:
        self._discord_token = token
        self._app_context = app_context

        self._bot = hikari.GatewayBot(intents=hikari.Intents.ALL, token=self._discord_token)
        self._events = DiscordEvents(self._app_context)

        self._bot.subscribe(hikari.GuildAvailableEvent, self._events.on_guild_available)
        self._bot.subscribe(hikari.GuildJoinEvent, self._events.on_guild_join)
        self._bot.subscribe(hikari.GuildMessageCreateEvent, self._events.on_message)

    async def run(self) -> None:
        try:
            await self._bot.start()
            await self._bot.join()
        finally:
            await self._bot.close()