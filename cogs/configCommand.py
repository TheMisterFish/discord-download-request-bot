from discord.ext import commands
from discord.commands import Option, SlashCommandGroup

from core.config import load_config, save_config
from core.guards import is_admin
from core.logger import command_logger

class ConfigCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    config = SlashCommandGroup("config", "Configure bot settings")

    @config.command(name="cooldown", description="Configure cooldown settings for the /download and /dn command")
    @is_admin()
    @command_logger
    async def config_cooldown(
        self,
        ctx,
        cooldown_limit: Option(int, "Set the cooldown limit", required=True),
        cooldown_timeout: Option(int, "Set the cooldown timeout in seconds", required=True)
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)
        
        config['cooldown'] = {
            'limit': cooldown_limit,
            'timeout': cooldown_timeout
        }
        
        save_config(server_id, config)

        self.bot.dispatch('config_update')
        
        # Update the cooldown for the DownloadCommand
        download_cog = self.bot.get_cog('DownloadCommand')
        if download_cog:
            download_cog.config = config
        
        await ctx.respond(f"Cooldown configuration updated. Limit: {cooldown_limit}, Timeout: {cooldown_timeout} seconds", ephemeral=True)

    @config.command(name="admin_download", description="Configure admin download permissions")
    @is_admin()
    async def config_admin_download(
        self,
        ctx,
        allow_admin_download: Option(bool, "Allow admins to always use /download & /dn", required=True)
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)
        
        config['admin_always_download'] = allow_admin_download
        
        save_config(server_id, config)
        
        await ctx.respond(f"Admin download permission updated. Admins can {'always' if allow_admin_download else 'not always'} use /download", ephemeral=True)

def setup(bot):
    bot.add_cog(ConfigCommand(bot))