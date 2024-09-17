import discord
from discord.ext import commands
from discord.commands import Option

from core.guards import is_moderator
from core.config import load_config, save_config

from core.logger import command_logger

class AllowDownloadCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="allowdownload", description="Manage allowed channels to download from")
    @is_moderator()
    @command_logger
    async def allowdownload(
        self, 
        ctx, 
        action: Option(str, "Choose an action", choices=["add", "remove", "list"]),
        channel: Option(discord.TextChannel, "Select a channel", required=False) = None
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)
        
        if 'allowed_channels' not in config:
            config['allowed_channels'] = {}

        if action == "add":
            if channel:
                if str(channel.id) not in config['allowed_channels']:
                    config['allowed_channels'][str(channel.id)] = channel.name
                    save_config(server_id, config)
                    await ctx.respond(f"✅ Added **{channel.name}** to allowed channels to download from", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is already an allowed channel to download from", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to add.", ephemeral=True)

        elif action == "remove":
            if channel:
                if str(channel.id) in config['allowed_channels']:
                    del config['allowed_channels'][str(channel.id)]
                    save_config(server_id, config)
                    await ctx.respond(f"✅ Removed **{channel.name}** from allowed channels to download from", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is not an allowed channel to download from", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to remove.", ephemeral=True)

        elif action == "list":
            if not config['allowed_channels']:
                await ctx.respond("No downloadable channels are currently configured. Meaning /download and /dn can be used in all text channels.", ephemeral=True)
                return

            allowed_channels = [f"• <#{channel_id}> ({channel_name})" for channel_id, channel_name in config['allowed_channels'].items()]
            embed = discord.Embed(title="🆗 Allowed channels to download from:", color=discord.Color.blue())
            embed.description = "\n".join(allowed_channels)
            await ctx.respond(embed=embed, ephemeral=True)

        else:
            await ctx.respond("Invalid action. Please choose 'add', 'remove', or 'list'.", ephemeral=True)

def setup(bot):
    bot.add_cog(AllowDownloadCommand(bot))