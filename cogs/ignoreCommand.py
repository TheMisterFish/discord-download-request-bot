import discord
from discord.ext import commands
from discord.commands import Option

from core.guards import is_moderator
from core.config import load_config, save_config
from core.logger import command_logger

class IgnoreCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="ignore", description="Ignore, unignore, or list ignored users")
    @is_moderator()
    @command_logger
    async def ignore(
        self, 
        ctx, 
        action: Option(str, "Choose to add, remove, or list ignored users", choices=["add", "remove", "list"]),
        user: Option(discord.Member, "The user to ignore or unignore", required=False) = None
    ):
        server_id = ctx.guild.id
        config = load_config(server_id)
        if 'ignored_users' not in config:
            config['ignored_users'] = {}

        if action == "add":
            if not user:
                await ctx.respond("You must specify a user to ignore.", ephemeral=True)
                return
            if user.guild_permissions.administrator or (user.guild_permissions.manage_messages and user.guild_permissions.kick_members):
                await ctx.respond(f"❌ Cannot ignore an admin. **{user.name}** is an administrator.", ephemeral=True)
                return

            if str(user.id) not in config['ignored_users']:
                config['ignored_users'][str(user.id)] = user.name

                save_config(server_id, config)
                await ctx.respond(f"✅ Now ignoring user: **{user.name}**", ephemeral=True)
            else:
                await ctx.respond(f"Already ignoring user: **{user.name}**", ephemeral=True)

        elif action == "remove":
            if not user:
                await ctx.respond("You must specify a user to unignore.", ephemeral=True)
                return
            if str(user.id) in config['ignored_users']:
                del config['ignored_users'][str(user.id)]
                save_config(server_id, config)
                await ctx.respond(f"✅ User **{user.name}** is no longer ignored.", ephemeral=True)
            else:
                await ctx.respond(f"User **{user.name}** is not currently ignored.", ephemeral=True)

        elif action == "list":
            if not config['ignored_users']:
                await ctx.respond("No users are currently ignored.", ephemeral=True)
                return

            ignored_users = [f"{username} (ID: {user_id})" for user_id, username in config['ignored_users'].items()]
            embed = discord.Embed(title="🤐 Ignored Users", color=discord.Color.blue())
            embed.description = "\n".join(ignored_users)
            await ctx.respond(embed=embed, ephemeral=True)

        else:
            await ctx.respond("Invalid action. Please choose 'add', 'remove', or 'list'.")
      

def setup(bot):
    bot.add_cog(IgnoreCommand(bot))