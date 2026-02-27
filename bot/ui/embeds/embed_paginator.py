import discord
from discord import ui, Interaction
from discord.ext import commands

from core.dto.embed_paginator_data import EmbedPaginatorData

class EmbedPaginator(ui.View):
    def __init__(self,
                 ctx: commands.Context | discord.Interaction,
                 data: EmbedPaginatorData,
                 start_page: int = 1,
                 items_per_page: int = 10,
                 timeout: int = 60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.data = data
        self.items_per_page = items_per_page
        self.message: discord.Message | None = None

        row_count = len(next(iter(self.data.data.values())))
        self.max_pages = (row_count + self.items_per_page - 1) // self.items_per_page

        start_page = 0 if start_page < 1 else start_page - 1
        self.page = min(start_page, self.max_pages - 1)

        if self.max_pages > 1:
            self.start_btn: ui.Button = ui.Button(label='«', style=discord.ButtonStyle.gray)
            self.prev_btn: ui.Button = ui.Button(label='◄', style=discord.ButtonStyle.red)
            self.next_btn: ui.Button = ui.Button(label='►', style=discord.ButtonStyle.green)
            self.end_btn: ui.Button = ui.Button(label='»', style=discord.ButtonStyle.gray)

            self.start_btn.callback = self.on_start  # type: ignore[method-assign]
            self.prev_btn.callback = self.on_prev  # type: ignore[method-assign]
            self.next_btn.callback = self.on_next  # type: ignore[method-assign]
            self.end_btn.callback = self.on_end  # type: ignore[method-assign]

            self.page_info_btn: ui.Button = ui.Button(label=f'1/12', style=discord.ButtonStyle.gray, disabled=True)

            self.add_item(self.start_btn)
            self.add_item(self.prev_btn)
            self.add_item(self.page_info_btn)
            self.add_item(self.next_btn)
            self.add_item(self.end_btn)

    async def handle(self, interaction: Interaction | None = None):
        embed, view = self.generate_message_content()
        await self.respond(embed, view, interaction=interaction)

    async def respond(self, embed: discord.Embed, view: ui.View | None = None, *,
                      interaction: Interaction | None = None):
        if interaction is not None:
            await interaction.response.edit_message(embed=embed, view=view)
            return

        if isinstance(self.ctx, discord.Interaction):
            if self.ctx.response.is_done():
                message = await self.ctx.followup.send(embed=embed, view=view, wait=True)  # type: ignore[call-overload]
            else:
                await self.ctx.response.send_message(embed=embed, view=view)  # type: ignore[arg-type]
                message = await self.ctx.original_response()
        else:
            message = await self.ctx.send(embed=embed, view=view)  # type: ignore[arg-type]

        self.message = message

    def generate_message_content(self, timed_out: bool = False) -> tuple[discord.Embed, ui.View | None]:
        start_idx = self.page * self.items_per_page
        end_idx = start_idx + self.items_per_page

        embed = discord.Embed(
            title=self.data.title,
            color=discord.Color.blue(),
        )

        if self.data.footer:
            if timed_out:
                embed.set_footer(text=f'{self.data.footer}\nTimed out')
            else:
                embed.set_footer(text=self.data.footer)
        elif not self.data.footer and timed_out:
            embed.set_footer(text='Timed out')

        for header, row in self.data.data.items():
            embed.add_field(name=header, value='\n'.join(map(str, row[start_idx:end_idx])))

        # No need for pagination controls in case there is only one page
        if self.max_pages > 1:
            self.update_button_disabled_state()
            self.page_info_btn.label = f'Page {self.page + 1}/{self.max_pages}'
            return embed, self

        return embed, None

    async def on_prev(self, interaction: Interaction):
        self.page -= 1
        await self.handle(interaction)

    async def on_next(self, interaction: Interaction):
        self.page += 1
        await self.handle(interaction)

    async def on_start(self, interaction: Interaction):
        self.page = 0
        await self.handle(interaction)

    async def on_end(self, interaction: Interaction):
        self.page = self.max_pages - 1
        await self.handle(interaction)

    def update_button_disabled_state(self):
        if self.page == 0:
            self.start_btn.disabled = True
            self.prev_btn.disabled = True
            self.next_btn.disabled = False
            self.end_btn.disabled = False
        elif self.page == self.max_pages - 1:
            self.start_btn.disabled = False
            self.prev_btn.disabled = False
            self.next_btn.disabled = True
            self.end_btn.disabled = True
        else:
            self.start_btn.disabled = False
            self.prev_btn.disabled = False
            self.next_btn.disabled = False
            self.end_btn.disabled = False

    async def interaction_check(self, interaction: Interaction) -> bool:
        author_id = self.ctx.user.id if isinstance(self.ctx, discord.Interaction) else self.ctx.author.id

        if interaction.user.id != author_id:
            await interaction.response.send_message('This embed does not belong to you, unable to interact with it.', ephemeral=True)
            return False

        return True

    async def on_timeout(self):
        if self.max_pages > 1:
            if self.message:
                embed, _ = self.generate_message_content(timed_out=True)

                for item in self.children:
                    item.disabled = True

                await self.message.edit(embed=embed, view=self)
        else:
            embed, _ = self.generate_message_content(timed_out=True)
            await self.message.edit(embed=embed)