import stoat

from app_context import AppContext
from messengers.stoat.events import StoatEvents

class StoatBot:
    def __init__(self, token: str, app_context: AppContext) -> None:
        self._token = token
        self._app_context = app_context

        self._bot = stoat.Client(token=self._token)
        self._events = StoatEvents(self._bot, self._app_context)
        self._bot.subscribe(stoat.ReadyEvent, self._events.on_ready)
        self._bot.subscribe(stoat.ServerCreateEvent, self._events.on_server_create)
        self._bot.subscribe(stoat.MessageCreateEvent, self._events.on_message)

    async def run(self) -> None:
        try:
            await self._bot.start()
        finally:
            await self._bot.close()