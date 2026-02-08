import discord

from core.dto.guild_config_update_result import GuildConfigUpdateResult


class GuildSetupEmbedFactory:
    @staticmethod
    def from_update_result(result: GuildConfigUpdateResult) -> discord.Embed:
        return (GuildSetupEmbedFactory._success_embed(result) if result.ok
                else GuildSetupEmbedFactory._error_embed(result))

    @staticmethod
    def _error_embed(result: GuildConfigUpdateResult) -> discord.Embed:
        return discord.Embed(
            title='Guild Configuration',
            color=discord.Color.dark_red(),
            description=(
                "Error in guild configuration.\n\n"
                f"**{result.error}**"
            )
        )

    @staticmethod
    def _success_embed(result: GuildConfigUpdateResult) -> discord.Embed:
        settings = result.settings
        listen_channel = f'<#{settings.listen_channel_id}>' if settings.listen_channel_id else 'Not set'

        return discord.Embed(
            title='Guild Configuration',
            color=discord.Color.dark_green(),
            description=(
                "Basic channel configuration done.\n\n"
                f"**Pickup channel:** <#{settings.pickup_channel_id}>\n"
                f"**Listen channel:** {listen_channel}"
            )
        )