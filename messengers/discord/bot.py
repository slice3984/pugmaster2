import hikari

from messengers.discord.events import DiscordEvents


class DiscordBot:
    def __init__(self, token: str) -> None:
        self._discord_token = token
        self._stoat_token = token

        self._bot = hikari.GatewayBot(intents=hikari.Intents.ALL, token=self._discord_token)
        self._events = DiscordEvents()

        self._bot.subscribe(hikari.GuildMessageCreateEvent, self._events.on_message)

    async def start(self) -> None:
        await self._bot.start()

    async def join(self) -> None:
        await self._bot.join()