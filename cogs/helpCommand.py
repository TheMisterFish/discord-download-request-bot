import discord
from discord.ext import commands

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
        
        embed = discord.Embed(title="ℹ️ Bot Help", color=discord.Color.blue())

        # User commands
        embed.add_field(name="__**User Commands**__", value="", inline=False)
        embed.add_field(name="/download [name] [id]", value="Search for a download by name or ID. Use either name or ID.", inline=False)
        embed.add_field(name="/dn <input>", value="Shortcut for /download. Enter download name or ID.", inline=False)
        embed.add_field(name="/video <title>", value="Search for a video by title.", inline=False)
        embed.add_field(name="/help", value="Shows this help message!", inline=False)

        if is_mod or is_admin:
            # Moderator commands
            embed.add_field(name="\u200b", value="", inline=False)
            embed.add_field(name="__**Moderator Commands**__", value="", inline=False)
            embed.add_field(name="/log [action] [limit] [page]", value="Download log file or view recent logs. Actions: download, view.", inline=False)
            embed.add_field(name="/config allowed_download_channels [action] [channel]", value="Manage allowed channels to download from (add, remove, list).", inline=False)
            embed.add_field(name="/config ignore [action] [user]", value="Ignore, unignore, or list ignored users.", inline=False)
            embed.add_field(name="/config videochannel [action] [channel]", value="Manage video channels (add, remove, scan, list).", inline=False)
            embed.add_field(name="/config downloadchannel [action] [channel]", value="Manage channels where download links can be found (add, remove, scan, list).", inline=False)

        if is_admin:
            # Admin commands
            embed.add_field(name="\u200b", value="", inline=False)
            embed.add_field(name="__**Admin Commands**__", value="", inline=False)
            embed.add_field(name="/config cooldown [limit] [timeout]", value="Configure cooldown settings for /download, /dn, and /video commands.", inline=False)
            embed.add_field(name="/config admin_download [allow]", value="Configure admin download permissions.", inline=False)
            embed.add_field(name="/config search_regex [regex]", value="Configure the search regex for download messages.", inline=False)
            embed.add_field(name="/config reset_regex", value="Reset the search regex to default (DN : (.+)).", inline=False)

        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(HelpCommand(bot))
