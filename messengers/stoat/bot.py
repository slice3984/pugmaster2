import stoat

from messengers.stoat.events import StoatEvents

class StoatBot:
    def __init__(self, token: str):
        self._token = token

        self._bot = stoat.Client(token=self._token)
        self._events = StoatEvents(self._bot)

        self._bot.subscribe(stoat.MessageCreateEvent, self._events.on_message)

    async def start(self):
        await self._bot.start()