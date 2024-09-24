import discord
from discord.ext import commands

from core.config import load_config, server_configs
from core.utils import process_download_message, process_video_message, scan_download_channel, scan_video_channel
from core.guards import UserIgnoredError, NotAllowedChannelError
from core.logger import get_server_logger

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user.name}')

        for guild in self.bot.guilds:
            server_id = guild.id
            serverLogger = get_server_logger(server_id)
            config = load_config(server_id)
            server_configs[server_id] = config

            serverLogger.logger.info(f'Bot is ready in guild: {guild.name} (ID: {server_id})')
            print(f'Bot is ready in guild: {guild.name} (ID: {server_id})')

            # # Disabled but kept it in. It automatically starts scanning on restart, but I don't think it's actually needed
            #
            # for channel_id, channel_name in config['download_channels'].items():
            #     channel = discord.utils.get(guild.channels, name=channel_name)
            #     if channel:
            #         await scan_download_channel(None, channel, server_id)
            #         logger.logger.info(f'Scanned download channel: {channel.name}')

            # for channel_id, channel_name in config['video_channels'].items():
            #     channel = discord.utils.get(guild.channels, name=channel_name)
            #     if channel:
            #         await scan_video_channel(None, channel, server_id)
            #         logger.logger.info(f'Scanned video channel: {channel.name}')

        print('Initialization complete')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        if message.guild is None:  # This is a DM
            await message.channel.send("This bot can only be used in servers, not in direct messages.")
            return

        server_id = message.guild.id
        
        if not server_id:
            raise commands.NoPrivateMessage("This command cannot be used in private messages.")
        
        config = server_configs.get(server_id) or load_config(server_id)
        serverLogger = get_server_logger(server_id)

        if str(message.author.id) in config['ignored_users']:
            return

        if str(message.channel.id) in config['download_channels']:
            serverLogger.logger.info(f"Processing download message in channel: {message.channel.name}")
            await process_download_message(message)

        if str(message.channel.id) in config['video_channels']:
            serverLogger.logger.info(f"Processing video message in channel: {message.channel.name}")
            await process_video_message(message)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        server_id = None
        
        if(ctx.guild):
            server_id = ctx.guild.id
            serverLogger = get_server_logger(server_id)
            config = server_configs.get(server_id) or load_config(server_id)

        if isinstance(error, Exception) and not isinstance(error, discord.DiscordException):
            if(server_id):
                serverLogger.logger.error(f"Error in command {ctx.command}: {str(error)}")
            print(f"Error in command {ctx.command}: {str(error)}")
            
            await ctx.respond(f"An error occurred: {str(error)}", ephemeral=True)
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.respond(f"This bot can only be used in servers, not in direct messages.", ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.respond("You don't have the necessary permissions to use this command.", ephemeral=True) 
        elif isinstance(error, UserIgnoredError):
            await ctx.respond("You cannot use this command at this time.", ephemeral=True)
        elif isinstance(error, NotAllowedChannelError):
            allowed_channels = config.get('allowed_channels', {})
            channel_links = ", ".join([f"<#{channel_id}>" for channel_id in allowed_channels.keys()])
            await ctx.respond(f"Please use the download command in the allowed text channels: {channel_links}.", ephemeral=True)
        else:
            await ctx.respond(f"An unexpected error occurred", ephemeral=True)

            if(server_id):
                serverLogger.logger.error(f"Unexpected error in command {ctx.command}: {str(error)}")

            print(f"Unexpected error in command {ctx.command}: {str(error)}")

def setup(bot):
    bot.add_cog(Events(bot))
