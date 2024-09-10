import discord
from discord.ext import commands
from discord.commands import Option

from core.guards import is_moderator
from core.config import load_config, save_config
from core.utils import scan_download_channel

from core.logger import command_logger

class DownloadChannelCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="downloadchannel", description="Manage channels where download links can be found")
    @is_moderator()
    @command_logger
    async def downloadchannel(
        self, 
        ctx, 
        action: Option(str, "Choose an action", choices=["add", "remove", "scan", "list"]),
        channel: Option(discord.TextChannel, "Select a channel", required=False) = None
    ):
        config = load_config()

        if 'download_channels' not in config:
            config['download_channels'] = {}

        if action == "add":
            if channel:
                if str(channel.id) not in config['download_channels']:
                    config['download_channels'][str(channel.id)] = channel.name
                    save_config(config)
                    await ctx.respond(f"✅ Added **{channel.name}** to download posts channels", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is already a download posts channel", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to add.", ephemeral=True)

        elif action == "remove":
            if channel:
                if str(channel.id) in config['download_channels']:
                    del config['download_channels'][str(channel.id)]
                    save_config(config)
                    await ctx.respond(f"✅ Removed **{channel.name}** from download posts channels", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is not a download posts channel", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to remove.", ephemeral=True)

        elif action == "scan":
            if channel:
                await ctx.respond(f"🔍 Scanning channel **{channel}**", ephemeral=True)
                await scan_download_channel(ctx, channel)
            else:
                await ctx.respond("🔍 Scanning all configured channels...", ephemeral=True)
                for channel_id, channel_name in config['download_channels'].items():
                    channel = discord.utils.get(ctx.guild.channels, name=channel_name)
                    if channel:
                        await scan_download_channel(ctx, channel)
                    else:
                        await ctx.followup.send(f"❌ Could not find channel: **{channel_name}**", ephemeral=True)
                await ctx.followup.send("✅ Scan completed for all configured channels.", ephemeral=True)

        elif action == "list":
            if 'download_channels' not in config or not config['download_channels']:
                await ctx.respond("No channels to get downloads from are currently configured.", ephemeral=True)
                return

            download_channels = [f"• <#{channel_id}> ({channel_name})" for channel_id, channel_name in config['download_channels'].items()]
            embed = discord.Embed(title=f"📋 Download Posts Channels", color=discord.Color.blue())
            embed.description = "\n".join(download_channels)
            await ctx.respond(embed=embed, ephemeral=True)

        else:
            await ctx.respond("Invalid action. Please choose 'add', 'remove', 'scan', or 'list'.", ephemeral=True)


def setup(bot):
    bot.add_cog(DownloadChannelCommand(bot))