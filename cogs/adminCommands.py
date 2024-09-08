import discord
from discord.ext import commands
from discord.commands import Option

from fuzzywuzzy import fuzz, process

from core.guards import is_admin, is_not_ignored
from core.config import load_config, save_config
from core.utils import scan_channel

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="ignore", description="Ignore, unignore, or list ignored users")
    @is_admin()
    @is_not_ignored()
    async def ignore(
        self, 
        ctx, 
        action: Option(str, "Choose to add, remove, or list ignored users", choices=["add", "remove", "list"]),
        user: Option(discord.Member, "The user to ignore or unignore", required=False) = None
    ):
        config = load_config()
        if 'ignored_users' not in config:
            config['ignored_users'] = {}

        if action == "add":
            if not user:
                await ctx.respond("You must specify a user to ignore.", ephemeral=True)
                return
            if user.guild_permissions.administrator:
                await ctx.respond(f"❌ Cannot ignore an admin. **{user.name}** is an administrator.", ephemeral=True)
                return

            if str(user.id) not in config['ignored_users']:
                config['ignored_users'][str(user.id)] = user.name
                save_config(config)
                await ctx.respond(f"✅ Now ignoring user: **{user.name}**", ephemeral=True)
            else:
                await ctx.respond(f"Already ignoring user: **{user.name}**", ephemeral=True)

        elif action == "remove":
            if not user:
                await ctx.respond("You must specify a user to unignore.", ephemeral=True)
                return
            if str(user.id) in config['ignored_users']:
                del config['ignored_users'][str(user.id)]
                save_config(config)
                await ctx.respond(f"✅ User **{user.name}** is no longer ignored.", ephemeral=True)
            else:
                await ctx.respond(f"User **{user.name}** is not currently ignored.", ephemeral=True)

        elif action == "list":
            if not config['ignored_users']:
                await ctx.respond("No users are currently ignored.", ephemeral=True)
                return

            ignored_users = [f"{username} (ID: {user_id})" for user_id, username in config['ignored_users'].items()]
            embed = discord.Embed(title="Ignored Users", color=discord.Color.blue())
            embed.description = "\n".join(ignored_users)
            await ctx.respond(embed=embed, ephemeral=True)
    
    @commands.slash_command(name="linkchannel", description="Manage link channels")
    @is_admin()
    @is_not_ignored()
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
    bot.add_cog(AdminCommands(bot))