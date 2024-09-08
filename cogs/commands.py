import discord
from discord.ext import commands
from discord.commands import Option

from core.guards import is_admin, is_not_ignored
from core.config import load_config, save_config
from core.utils import get_entry, scan_channel

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="download", description="Search for a download id")
    @is_not_ignored()
    async def download(self, ctx, id: str):
        name, links = get_entry(str(id).upper())
        if name:
            embed = discord.Embed(
                title=f"Found: {name}",
                color=discord.Color.green()
            )
            
            for channel, link in links.items():
                embed.add_field(name=channel, value=link, inline=False)
            
            await ctx.respond(embed=embed)
        else:
            error_embed = discord.Embed(
                title="Download ID Not Found",
                description="Sorry, could not find a link for this download id. It might be released at a later point.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=error_embed)

    @commands.slash_command(name="ignore", description="Ignore a user")
    @is_admin()
    @is_not_ignored()
    async def ignore(self, ctx, user: discord.Member):
        if user.guild_permissions.administrator:
            await ctx.respond(f"❌ Cannot ignore an admin. **{user.name}** is an administrator.", ephemeral=True)
            return

        config = load_config()
        if str(user.id) not in config['ignored_users']:
            config['ignored_users'].append(str(user.id))
            save_config(config)
            await ctx.respond(f"✅ Now ignoring user: **{user.name}**", ephemeral=True)
        else:
            await ctx.respond(f"Already ignoring user: **{user.name}**", ephemeral=True)

    @commands.slash_command(name="linkchannel", description="Manage link channels")
    @is_admin()
    @is_not_ignored()
    async def linkchannel(
        self, 
        ctx, 
        action: Option(str, "Choose an action", choices=["add", "remove", "scan"]),
        channel: Option(discord.TextChannel, "Select a channel", required=False) = None
    ):
        config = load_config()

        if action == "add":
            if channel:
                if channel.name not in config['link_channels']:
                    config['link_channels'].append(channel.name)
                    save_config(config)
                    await ctx.respond(f"✅ Added **{channel.name}** to link channels")
                else:
                    await ctx.respond(f"**{channel.name}** is already a link channel")
            else:
                await ctx.respond("Please specify a channel to add.")
        elif action == "remove":
            if channel:
                if channel.name in config['link_channels']:
                    config['link_channels'].remove(channel.name)
                    save_config(config)
                    await ctx.respond(f"✅ Removed **{channel.name}** from link channels")
                else:
                    await ctx.respond(f"**{channel.name}** is not a link channel")
            else:
                await ctx.respond("Please specify a channel to remove.")
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

def setup(bot):
    bot.add_cog(Commands(bot))