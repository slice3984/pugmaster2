import hikari

from app_context import AppContext
from dto.messenger import MessengerRegistration
from enums import MessengerType


class DiscordEvents:
    def __init__(self, app_context: AppContext):
        self._app_context = app_context

    async def on_guild_available(self, event: hikari.GuildAvailableEvent):
        await self._register_guild(event)

    async def on_guild_join(self, event: hikari.GuildJoinEvent):
        await self._register_guild(event)

    async def on_message(
            self,
            event: hikari.GuildMessageCreateEvent,
    ):
        if event.is_bot or not event.content:
            return

    async def _register_guild(self, event: hikari.GuildAvailableEvent | hikari.GuildJoinEvent):
        await self._app_context.state_service.handle_messenger_registration(
            messenger_registration=MessengerRegistration(
                messenger_type=MessengerType.DISCORD,
                server_uid=str(event.guild_id),
                name=event.guild.name
            )
        )