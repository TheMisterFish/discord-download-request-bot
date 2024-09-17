import discord
from discord.ext import commands
from discord.commands import Option

from core.guards import is_not_ignored, in_allowed_channel
from core.database import get_server_database
from core.logger import command_logger

class VideoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def video_title_autocomplete(self, ctx: discord.AutocompleteContext):
        server_id = ctx.interaction.guild_id
        db = get_server_database(server_id)
        return db.get_video_names(100, ctx.value, 0)

    @commands.slash_command(name="video", description="Search for a video by title")
    @is_not_ignored()
    @in_allowed_channel()
    @command_logger
    async def video(
        self,
        ctx,
        title: Option(str, "Enter the video title", autocomplete=video_title_autocomplete, required=True)
    ):
        server_id = ctx.guild.id
        db = get_server_database(server_id)

        matching_videos = db.get_matching_videos(100, title, 90)

        if not matching_videos:
            await ctx.respond("No videos found matching your query.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Found {len(matching_videos)} video{'s' if len(matching_videos) > 1 else ''}:",
            color=discord.Color.green()
        )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        footer_text = f"Requested by {ctx.author.display_name}"
        user_avatar_url = ctx.author.display_avatar.url if ctx.author.display_avatar else None
        embed.set_footer(text=footer_text, icon_url=user_avatar_url)

        if len(matching_videos) > 5:
            await ctx.respond("Too many results found. Please be more specific in your query.", ephemeral=True)
            return
    
        for video in matching_videos[:5]:
            name = video['name']
            links = video['links']
            tag = video.get('tag', 'No tag')
            
            first_link = next(iter(links.values()))
            
            linked_name = f"[{name}]({first_link})"
            
            embed.add_field(name=linked_name, value=f"*{tag}*", inline=False)

        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_config_update(self, server_id):
        pass

def setup(bot):
    bot.add_cog(VideoCommand(bot))
