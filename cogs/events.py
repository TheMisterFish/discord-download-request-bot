import discord
from discord.ext import commands
from discord import ApplicationContext
from discord.errors import ApplicationCommandInvokeError

from core.config import load_config
from core.utils import process_message, scan_channel
from core.guards import UserIgnoredError, NotAllowedChannelError

from core.logger import logger

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'Logged in as {self.bot.user.name}')
        config = load_config()
        for channel_name in config['link_channels']:
            channel = discord.utils.get(self.bot.get_all_channels(), name=channel_name)
            if channel:
                await scan_channel(None, channel)
        logger.info('Initialization complete')
        print('Initialization complete')


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        config = load_config()
        if str(message.author.id) in config['ignored_users']:
            return

        if message.channel.name in config['link_channels']:
            logger.info(f"Processing message in channel: {message.channel.name}")
            await process_message(message)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, Exception) and not isinstance(error, discord.DiscordException):
            logger.error(f"Error in command {ctx.command}: {str(error)}")
            print(f"Error in command {ctx.command}: {str(error)}")
            
            await ctx.respond(f"An error occurred: {str(error)}", ephemeral=True)
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.respond("You don't have the necessary permissions to use this command.", ephemeral=True) 
        elif isinstance(error, UserIgnoredError):
            await ctx.respond("You cannot use this command at this time.", ephemeral=True)
        elif isinstance(error, NotAllowedChannelError):
            allowed_channels = load_config().get('allowed_channels', {})
            channel_links = ", ".join([f"<#{channel_id}>" for channel_id in allowed_channels.keys()])
            await ctx.respond(f"Please use the download command in the allowed text channels: {channel_links}.", ephemeral=True)
        else:
            await ctx.respond(f"An unexpected error occurred", ephemeral=True)
            logger.error(f"Unexpected error in command {ctx.command}: {str(error)}")
            print(f"Unexpected error in command {ctx.command}: {str(error)}")

def setup(bot):
    bot.add_cog(Events(bot))