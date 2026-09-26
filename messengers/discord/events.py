import hikari


class DiscordEvents:
    def __init__(self):
        pass

    async def on_message(
            self,
            event: hikari.GuildMessageCreateEvent,
    ):
        if event.is_bot or not event.content:
            return

