import discord
from discord.ext import commands
from discord.commands import Option

from core.guards import is_moderator
from core.config import load_config, save_config
from core.utils import scan_video_channel
from core.logger import command_logger

class VideoChannelCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="videochannel", description="Manage video channels")
    @is_moderator()
    @command_logger
    async def videochannel(
        self, 
        ctx, 
        action: Option(str, "Choose an action", choices=["add", "remove", "scan", "list"]),
        channel: Option(discord.TextChannel, "Select a channel", required=False) = None
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)

        if 'video_channels' not in config:
            config['video_channels'] = {}

        if action == "add":
            if channel:
                if str(channel.id) not in config['video_channels']:
                    config['video_channels'][str(channel.id)] = channel.name
                    save_config(server_id, config)
                    await ctx.respond(f"✅ Added **{channel.name}** to video channels", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is already a video channel", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to add.", ephemeral=True)

        elif action == "remove":
            if channel:
                if str(channel.id) in config['video_channels']:
                    del config['video_channels'][str(channel.id)]
                    save_config(server_id, config)
                    await ctx.respond(f"✅ Removed **{channel.name}** from video channels", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is not a video channel", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to remove.", ephemeral=True)

        elif action == "scan":
            if channel:
                await ctx.respond(f"🔍 Scanning video channel **{channel}**", ephemeral=True)
                await scan_video_channel(ctx, channel)
            else:
                await ctx.respond("🔍 Scanning all configured video channels...", ephemeral=True)
                for channel_id, channel_name in config['video_channels'].items():
                    channel = discord.utils.get(ctx.guild.channels, name=channel_name)
                    if channel:
                        await scan_video_channel(ctx, channel)
                    else:
                        await ctx.followup.send(f"❌ Could not find channel: **{channel_name}**", ephemeral=True)
                await ctx.followup.send("✅ Scan completed for all configured video channels.", ephemeral=True)

        elif action == "list":
            if 'video_channels' not in config or not config['video_channels']:
                await ctx.respond("No video channels are currently configured.", ephemeral=True)
                return

            video_channels = [f"• <#{channel_id}> ({channel_name})" for channel_id, channel_name in config['video_channels'].items()]
            embed = discord.Embed(title=f"📋 Video Channels", color=discord.Color.blue())
            embed.description = "\n".join(video_channels)
            await ctx.respond(embed=embed, ephemeral=True)

        else:
            await ctx.respond("Invalid action. Please choose 'add', 'remove', 'scan', or 'list'.", ephemeral=True)

def setup(bot):
    bot.add_cog(VideoChannelCommand(bot))