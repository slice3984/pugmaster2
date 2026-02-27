import discord
from discord import ui, Interaction

from domain.types import GuildId
from managers.guild_state_manager import GuildStateManager
from managers.logic.queue_config import RemoveQueuesPlan

class ConfirmRemoveQueuesView(ui.View):
    def __init__(
            self,
            interaction: Interaction,
            guild_state_manager: GuildStateManager,
            plan: RemoveQueuesPlan,
    ):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.facade = guild_state_manager.queue_configs
        self.guild_state_manager = guild_state_manager
        self.plan = plan
        self.message: discord.InteractionMessage | None = None

        self.confirm_btn: ui.Button = ui.Button(label="Remove queues", style=discord.ButtonStyle.danger)
        self.cancel_btn: ui.Button = ui.Button(label="Cancel", style=discord.ButtonStyle.green)

        self.confirm_btn.callback = self.on_confirm  # type: ignore[method-assign]
        self.cancel_btn.callback = self.on_cancel  # type: ignore[method-assign]

        self.add_item(self.confirm_btn)
        self.add_item(self.cancel_btn)

    async def on_confirm(self, interaction: Interaction):
        # Actual removal, rechecks the queues to be removed
        plan = await self.facade.apply_remove_queues(guild_id=GuildId(interaction.guild_id), queues=self.plan.to_remove)

        if len(plan.to_remove) == 0:
            await interaction.response.edit_message(embed=self._generate_no_removes_embed(), view=None)
            self.stop()
            self._release_prompt_lease()
            return

        await interaction.response.edit_message(embed=self._generate_confirmation_embed(plan), view=None)
        self.stop()
        self._release_prompt_lease()

    async def on_cancel(self, interaction: Interaction):
        await interaction.response.edit_message(
            embed=discord.Embed(title="Cancelled queue removal.", color=discord.Color.green()),
            view=None,
        )
        self.stop()
        self._release_prompt_lease()

    def _generate_confirmation_embed(self, plan: RemoveQueuesPlan) -> discord.Embed:
        return discord.Embed(
            title="Queues removed",
            color=discord.Color.green(),
            description=(
                'Queue removal confirmed, removed queues:\n'
                f'{', '.join([f'**{q}**' for q in plan.to_remove])}'
            )
        )

    def _generate_no_removes_embed(self) -> discord.Embed:
        return discord.Embed(
            title='Queue removal failed',
            color=discord.Color.red(),
            description='Provided queues are not stored, nothing to remove.'
        )

    async def dialog(self) -> None:
        assert self.interaction.guild_id is not None

        prompt_lease = self.guild_state_manager.try_acquire_prompt_lease(
            guild_id=GuildId(self.interaction.guild_id),
            prompt_type='QueueRemovalPrompt'
        )

        if not prompt_lease:
            await self.interaction.response.send_message(
                'A queue removal prompt is already in progress.\nPlease wait until the operation is completed.',
                ephemeral=True)
            return None

        if len(self.plan.to_remove) == 0:
            await self.interaction.response.send_message(embed=self._generate_no_removes_embed(), ephemeral=True)
            return None

        embed = discord.Embed(
            title='Confirm queue removal',
            color=discord.Color.red(),
            description=(
                'Removing queues results in:\n'
                '- Deletion of all stats associated with the given queues\n'
                '- Queue specific ratings deleted\n'
                '- Players added to the given queues to be removed\n'
                '**This action cannot be undone!**\n\n'
                f'Affected queues: {', '.join([f'**{q}**' for q in self.plan.to_remove])}'
            )
        )

        embed.set_footer(text='This prompt will be active for 60 seconds.')

        await self.interaction.response.send_message(embed=embed, view=self, ephemeral=True)
        self.message = await self.interaction.original_response()
        return None

    def _release_prompt_lease(self):
        self.guild_state_manager.release_prompt_lease(
            guild_id=GuildId(self.interaction.guild_id),
            prompt_type='QueueRemovalPrompt'
        )

    async def on_timeout(self):
            await self.message.edit(
                embed=discord.Embed(
                    title="Queue removal - timed out",
                    color=discord.Color.red(),
                    description='Prompt timed out, please run the command again.'
                ),
                view=None
            )

            self._release_prompt_lease()