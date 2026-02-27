import discord

from domain.guild_state import QueueState


class QueuesEmbedFactory:
    @staticmethod
    def list_queues(queues: dict[str, QueueState]) -> discord.Embed:
        queue_names: list[str] = []
        player_counts: list[str] = []

        return discord.Embed()

