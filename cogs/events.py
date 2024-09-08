import discord
from discord.ext import commands
from discord import ApplicationContext
from discord.errors import ApplicationCommandInvokeError

from core.config import load_config
from core.utils import process_message, scan_channel

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user.name}')
        config = load_config()
        for channel_name in config['link_channels']:
            channel = discord.utils.get(self.bot.get_all_channels(), name=channel_name)
            if channel:
                await scan_channel(None, channel)
        print('Initialization complete')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        config = load_config()
        if str(message.author.id) in config['ignored_users']:
            return

        if message.channel.name in config['link_channels']:
            await process_message(message)

    @commands.Cog.listener()
    async def on_application_command_error(ctx: ApplicationContext, error: ApplicationCommandInvokeError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("You are missing Administrator permission(s) to run this command.", ephemeral=True)
        elif isinstance(error, UserIgnoredError):
            await ctx.respond("You are currently ignored and cannot use bot commands.", ephemeral=True)
        else:
            # Handle other types of errors or raise them
            raise error

def setup(bot):
    bot.add_cog(Events(bot))