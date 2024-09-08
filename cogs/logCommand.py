import discord
from discord.ext import commands
from discord import Option
import os

from core.guards import is_admin

class LogCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_file_path = 'data/logs/bot_commands.log'

    @commands.slash_command(name="log", description="Download log file or view recent logs")
    @is_admin()
    async def log(
        self,
        ctx: discord.ApplicationContext,
        action: Option(str, "Choose action", choices=["download", "view"], required=True),
        limit: Option(int, "Number of lines to view (for 'view' action)", min_value=1, max_value=100, required=False) = 10,
        page: Option(int, "page to offset to(for 'view' action)", min_value=0, max_value=100, required=False) = 0
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
            with open(self.log_file_path, 'r') as file:
                lines = file.readlines()
                
                start_index = max(0, len(lines) - (limit * page) - limit)

                selected_lines = lines[start_index:start_index + limit]
                log_content = ''.join(selected_lines)

            if len(log_content) > 1980:
                await ctx.respond("Log content is too long. Please use a smaller limit or download the full log.", ephemeral=True)
            else:
                await ctx.respond(f"{limit} log entries (offset by {limit * page}):\n```\n{log_content}\n```", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"An error occurred while reading the log file: {str(e)}", ephemeral=True)


def setup(bot):
    bot.add_cog(LogCommand(bot))