import discord
from discord.ext import commands
from discord import Option

import os

from core.logger import command_logger
from core.guards import is_moderator

class LogPaginationView(discord.ui.View):
    def __init__(self, cog, ctx, limit, page, timeout=60):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.ctx = ctx
        self.limit = limit
        self.page = page

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary, emoji="⬅️")
    async def previous_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page = max(1, self.page - 1)
        await interaction.response.edit_message(embed=await self.cog.create_log_embed(self.limit, self.page), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary, emoji="➡️")
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page += 1
        new_embed = await self.cog.create_log_embed(self.limit, self.page)
        if new_embed:
            await interaction.response.edit_message(embed=new_embed, view=self)
        else:
            self.page -= 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

class LogCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_file_path = 'data/logs/bot_commands.log'

    @commands.slash_command(name="log", description="Download log file or view recent logs")
    @is_moderator()
    @command_logger
    async def log(
        self,
        ctx: discord.ApplicationContext,
        action: Option(str, "Choose action", choices=["download", "view"], required=True),
        limit: Option(int, "Number of lines to view (for 'view' action)", min_value=1, max_value=100, required=False) = 10,
        page: Option(int, "Page to offset to (for 'view' action)", min_value=1, max_value=100, required=False) = 1
    ):
        if action == "download":
            await self.download_log(ctx)
        elif action == "view":
            await self.view_log(ctx, limit, page)

    async def download_log(self, ctx):
        if not os.path.exists(self.log_file_path):
            await ctx.respond("Log file not found.", ephemeral=True)
            return

        try:
            await ctx.respond("Here's the log file:", file=discord.File(self.log_file_path), ephemeral=True)
        except Exception as e:
            await ctx.respond(f"An error occurred while sending the log file: {str(e)}", ephemeral=True)

    async def view_log(self, ctx, limit, page):
        if not os.path.exists(self.log_file_path):
            await ctx.respond("Log file not found.", ephemeral=True)
            return

        try:
            embed = await self.create_log_embed(limit, page)
            if embed:
                view = LogPaginationView(self, ctx, limit, page)
                await ctx.respond(embed=embed, view=view, ephemeral=True)
            else:
                await ctx.respond("No log entries found.", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"An error occurred while reading the log file: {str(e)}", ephemeral=True)

    async def create_log_embed(self, limit, page):
        with open(self.log_file_path, 'r') as file:
            lines = file.readlines()

        total_pages = (len(lines) + limit - 1) // limit
        page = min(max(1, page), total_pages)

        start_index = max(0, len(lines) - (page * limit))
        end_index = start_index + limit

        selected_lines = lines[start_index:end_index]
        if not selected_lines:
            return None

        log_content = ''.join(selected_lines)

        embed = discord.Embed(title="Log Entries", color=discord.Color.blue())
        embed.description = f"```\n{log_content}\n```"
        embed.set_footer(text=f"Page {page}/{total_pages} | {limit} entries per page")

        return embed

def setup(bot):
    bot.add_cog(LogCommand(bot))
