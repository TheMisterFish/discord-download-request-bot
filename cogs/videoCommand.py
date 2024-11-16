from core.utils import truncate_with_dots
import discord

from discord.ext import commands
from discord.commands import Option
from discord.ext.commands import CooldownMapping, BucketType

from core.guards import is_not_ignored, in_allowed_channel
from core.database import get_server_database
from core.logger import command_logger
from core.config import load_config

class VideoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown_mappings = {}

    def get_cooldown_mapping(self, server_id):
        if server_id not in self.cooldown_mappings:
            config = load_config(server_id)
            self.cooldown_mappings[server_id] = CooldownMapping.from_cooldown(
                config.get('cooldown', {}).get('limit', 1),
                config.get('cooldown', {}).get('timeout', 3),
                BucketType.user
            )
        return self.cooldown_mappings[server_id]

    async def check_cooldown(self, ctx):
        server_id = ctx.guild.id
        bucket = self.get_cooldown_mapping(server_id).get_bucket(ctx)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after, BucketType.user)
        return True

    async def video_title_autocomplete(self, ctx: discord.AutocompleteContext):
        server_id = ctx.interaction.guild_id
        if not server_id:
            return []
        db = get_server_database(server_id)
        return [truncate_with_dots(id, 100) for id in db.get_video_names(100, ctx.value)]

    @commands.slash_command(name="video", description="Search for a video by title")
    @is_not_ignored()
    @in_allowed_channel()
    @command_logger
    async def video(
        self,
        ctx,
        title: Option(str, "Enter the video title", autocomplete=video_title_autocomplete, required=True)
    ):
        await self.check_cooldown(ctx)
        
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
            name = truncate_with_dots(video['name'], 256)
            links = video['links']
            tag = video.get('tag', 'No tag')
            
            linked_name = self.create_linked_name(name, links)
            
            embed.add_field(name=linked_name, value=f"*{tag}*", inline=False)

        await ctx.respond(embed=embed)

    def create_linked_name(self, name, links):
        if not links:
            return name

        linked_name = name + " ("
        
        urls = list(links.values())
        if len(urls) == 1:
            linked_name += urls[0]
        else:
            linked_name += ",".join(urls)
        
        linked_name += ")"
        return linked_name
    
    @video.error
    async def video_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.", ephemeral=True)
            return

    @commands.Cog.listener()
    async def on_config_update(self, server_id):
        if server_id in self.cooldown_mappings:
            del self.cooldown_mappings[server_id]

def setup(bot):
    bot.add_cog(VideoCommand(bot))
