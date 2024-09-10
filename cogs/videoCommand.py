import discord
from discord.ext import commands
from discord.commands import Option
from fuzzywuzzy import fuzz

from core.guards import is_not_ignored, in_allowed_channel
from core.datamanager import datamanager
from core.logger import command_logger
from core.config import load_config

class VideoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    async def video_title_autocomplete(self, ctx: discord.AutocompleteContext):
        return [name for name in datamanager.get_video_names() if ctx.value.lower() in name.lower()]

    @commands.slash_command(name="video", description="Search for a video by title")
    @is_not_ignored()
    @in_allowed_channel()
    @command_logger
    async def video(
        self,
        ctx,
        title: Option(str, "Enter the video title", autocomplete=video_title_autocomplete, required=True)
    ):
        def get_similarity(video_title, query_words):
            name = video_title.upper()
            
            if all(word.upper() in name for word in query_words):
                return 100
            
            return fuzz.partial_ratio(query_words.upper(), name)

        matching_videos = [
            video for video in datamanager.get_videos()
            if get_similarity(video['name'], title) >= 90
        ]


        matching_videos.sort(key=lambda x: get_similarity(x['name'], title), reverse=True)

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
    
        for video in matching_videos:
            name = video['name']
            links = video['links']
            tag = video.get('tag', 'No tag')
            
            first_link = next(iter(links.values()))
            
            linked_name = f"[{name}]({first_link})"
            
            embed.add_field(name=linked_name, value=f"*{tag}*", inline=False)

        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_config_update(self):
        self.config = load_config()

def setup(bot):
    bot.add_cog(VideoCommand(bot))