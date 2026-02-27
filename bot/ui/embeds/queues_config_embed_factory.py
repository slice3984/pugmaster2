import discord

from domain.queue_constants import MAX_QUEUE_NAME_LENGTH
from managers.facades.queue_configs import CreateQueuesResult

class QueuesConfigEmbedFactory:
    @staticmethod
    def create_queues(result: CreateQueuesResult) -> discord.Embed:
        if result.added_queues:
            embed = discord.Embed(
                title='Queue creation',
                description='You can edit individual queues with /manage_queues edit',
                color=discord.Color.green(),
            )

            queue_names: list[str] = []
            queue_player_counts: list[str] = []
            queue_team_counts: list[str] = []

            for queue in result.added_queues:
                queue_names.append(queue.name)
                queue_player_counts.append(str(queue.player_count))
                queue_team_counts.append(str(queue.team_count))

            embed.add_field(name='Name', value='\n'.join(queue_names))
            embed.add_field(name='Player Count', value='\n'.join(queue_player_counts))
            embed.add_field(name='Team Count', value='\n'.join(queue_team_counts))

        else:
            embed = discord.Embed(
                title='Queue creation failed',
                color=discord.Color.red(),
            )

        if result.errors:
            queue_lines = []
            error_lines = []

            for queue_name, errors in result.errors.items():
                for i, err in enumerate(errors):
                    if i == 0:
                        queue_lines.append(queue_name[:MAX_QUEUE_NAME_LENGTH])
                    else:
                        queue_lines.append(' ')

                    error_lines.append(err)

            embed.add_field(
                name='Failed queue',
                value="\n".join(queue_lines),
                inline=True,
            )

            embed.add_field(
                name='Error',
                value="\n".join(error_lines),
                inline=True,
            )

        return embed

    @staticmethod
    def no_valid_queues_provided():
        return discord.Embed(
            title='Queue creation failed',
            color=discord.Color.red(),
            description='No valid queues provided.',
        )

    @staticmethod
    def exceeded_creation_limit():
        return discord.Embed(
            title='Queue creation failed',
            color=discord.Color.red(),
            description='Exceeded the queue creation limit, up to 10 queues can be created at once.',
        )