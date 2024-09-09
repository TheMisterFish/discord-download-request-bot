import discord
from discord.ext import commands
from discord import Option

from core.logger import command_logger

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="help", description="Display available commands and their descriptions")
    @command_logger
    async def help(self, ctx):
        is_mod = False
        is_admin = False

        if ctx.author.guild_permissions.manage_messages and ctx.author.guild_permissions.kick_members:
            is_mod = True

        if ctx.author.guild_permissions.administrator:
            is_admin = True
        
        embed = discord.Embed(title="Bot Help", color=discord.Color.blue())

        # User commands
        embed.add_field(name="__**User Commands**__", value="", inline=False)
        embed.add_field(name="/download [name] [id]", value="Search for a farm by name or ID. Use either name or ID.", inline=False)
        embed.add_field(name="/dn <input>", value="Shortcut for /download. Enter farm name or ID.", inline=False)

        if is_mod or is_admin:
            # Moderator commands
            embed.add_field(name="\u200b", value="", inline=False)
            embed.add_field(name="__**Moderator Commands**__", value="", inline=False)
            embed.add_field(name="/log [action] [limit] [page]", value="Download log file or view recent logs.", inline=False)
            embed.add_field(name="/linkchannel [action] [channel]", value="Manage link channels (add, remove, scan, list).", inline=False)
            embed.add_field(name="/ignore [action] [user]", value="Ignore, unignore, or list ignored users.", inline=False)

        if is_admin:
            # Admin commands
            embed.add_field(name="\u200b", value="", inline=False)
            embed.add_field(name="__**Admin Commands**__", value="", inline=False)
            embed.add_field(name="/config cooldown [limit] [timeout]", value="Configure cooldown settings for /download and /dn commands.", inline=False)
            embed.add_field(name="/config admin_download [allow]", value="Configure admin download permissions.", inline=False)

        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(HelpCommand(bot))