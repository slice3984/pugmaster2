import stoat



class StoatEvents:
    def __init__(self, client: stoat.Client):
        self._bot = client

    async def on_message(self, event: stoat.MessageCreateEvent):
        msg = event.message
        channel = msg.channel

        if not isinstance(channel, stoat.TextChannel) or msg.author.bot is not None:
            return