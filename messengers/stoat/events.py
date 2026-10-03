import stoat

from app_context import AppContext
from dto.messenger import MessengerRegistration
from enums import MessengerType


class StoatEvents:
    def __init__(self, client: stoat.Client, app_context: AppContext):
        self._bot = client
        self._app_context = app_context

    async def on_ready(self, event: stoat.ReadyEvent):
        for server in event.servers:
            await self._register_server(server)

    async def on_server_create(self, event: stoat.ServerCreateEvent):
        await self._register_server(event.server)

    async def on_message(self, event: stoat.MessageCreateEvent):
        msg = event.message
        channel = msg.channel

        if not isinstance(channel, stoat.TextChannel) or msg.author.bot is not None:
            return

    async def _register_server(self, server: stoat.Server):
        await self._app_context.state_service.handle_messenger_registration(
            messenger_registration=MessengerRegistration(
                messenger_type=MessengerType.STOAT,
                server_uid=server.id,
                name=server.name
            )
        )