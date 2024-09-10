import discord
from discord.ext import commands
from discord.commands import Option

from core.guards import is_moderator
from core.config import load_config, save_config
from core.utils import scan_channel

from core.logger import command_logger

class LinkCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="linkchannel", description="Manage link channels")
    @is_moderator()
    @command_logger
    async def linkchannel(
        self, 
        ctx, 
        action: Option(str, "Choose an action", choices=["add", "remove", "scan", "list"]),
        channel: Option(discord.TextChannel, "Select a channel", required=False) = None
    ):
        config = load_config()

        if action == "add":
            if channel:
                if channel.name not in config['link_channels']:
                    config['link_channels'].append(channel.name)
                    save_config(config)
                    await ctx.respond(f"✅ Added **{channel.name}** to link channels", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is already a link channel", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to add.", ephemeral=True)

        elif action == "remove":
            if channel:
                if channel.name in config['link_channels']:
                    config['link_channels'].remove(channel.name)
                    save_config(config)
                    await ctx.respond(f"✅ Removed **{channel.name}** from link channels", ephemeral=True)
                else:
                    await ctx.respond(f"**{channel.name}** is not a link channel", ephemeral=True)
            else:
                await ctx.respond("Please specify a channel to remove.", ephemeral=True)

        elif action == "scan":
            if channel:
                await ctx.respond(f"🔍 Scanning channel **{channel}**", ephemeral=True)
                await scan_channel(ctx, channel)
            else:
                await ctx.respond("🔍 Scanning all configured channels...", ephemeral=True)
                for channel_name in config['link_channels']:
                    channel = discord.utils.get(ctx.guild.channels, name=channel_name)
                    if channel:
                        await scan_channel(ctx, channel)
                    else:
                        await ctx.followup.send(f"❌ Could not find channel: **{channel_name}**", ephemeral=True)
                await ctx.followup.send("✅ Scan completed for all configured channels.", ephemeral=True)

        elif action == "list":
            if 'link_channels' not in config or not config['link_channels']:
                await ctx.respond("No link channels are currently configured.", ephemeral=True)
                return

            link_channels = [f"• {channel}" for channel in config['link_channels']]
            embed = discord.Embed(title=f"📋 Link Channels", color=discord.Color.blue())
            embed.description = "\n".join(link_channels)
            await ctx.respond(embed=embed, ephemeral=True)

        else:
            await ctx.respond("Invalid action. Please choose 'add', 'remove', 'scan', or 'list'.", ephemeral=True)


def setup(bot):
    bot.add_cog(LinkCommand(bot))