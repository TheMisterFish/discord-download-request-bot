import discord
from discord.ext import commands
from discord.commands import Option
from discord.ext.commands import CooldownMapping, BucketType

from fuzzywuzzy import fuzz

from core.guards import is_not_ignored, in_allowed_channel
from core.utils import farm_autocomplete, id_autocomplete, farm_name_and_id_autocomplete
from core.database import get_download_entry
from core.datamanager import datamanager
from core.logger import command_logger
from core.config import load_config

class DownloadCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()
        self.update_cooldown_mapping()

    async def farm_name_autocomplete(self, ctx: discord.AutocompleteContext):
        return await farm_autocomplete(ctx, datamanager.get_farms())
    
    async def id_autocomplete(self, ctx: discord.AutocompleteContext):
        return await id_autocomplete(ctx, datamanager.get_farm_ids())

    async def farm_name_and_id_autocomplete(self, ctx: discord.AutocompleteContext):
        return await farm_name_and_id_autocomplete(ctx, datamanager.get_farm_ids(), datamanager.get_farms())

    def update_cooldown_mapping(self):
        self.cooldown_mapping = CooldownMapping.from_cooldown(
            self.config.get('cooldown', {}).get('limit', 1),
            self.config.get('cooldown', {}).get('timeout', 3),
            BucketType.user
        )
        
    async def check_cooldown(self, ctx):
        bucket = self.cooldown_mapping.get_bucket(ctx)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after, BucketType.user)
        return True

    @commands.slash_command(name="download", description="Search for a farm by name or ID")
    @is_not_ignored()
    @in_allowed_channel()
    @command_logger
    async def download(
        self,
        ctx,
        name: Option(str, "Enter the farm name", autocomplete=farm_name_autocomplete, required=False) = None,
        id: Option(str, "Enter the download ID", autocomplete=id_autocomplete, required=False) = None
    ):
        await self.check_cooldown(ctx)

        if id:
            await self.download_by_id(ctx, id)
        elif name:
            await self.download_by_query(ctx, name)
        else:
            await ctx.respond("Please provide either a farm name, ID, or search name.", ephemeral=True)

    @commands.slash_command(name="dn", description="Search for a farm by name or ID (shortcut)")
    @is_not_ignored()
    @in_allowed_channel()
    @command_logger
    async def dn(
        self,
        ctx,
        input: Option(str, "Enter the farm name or id", autocomplete=farm_name_and_id_autocomplete, required=True)
    ):
        await self.check_cooldown(ctx)
        name, links = get_download_entry(str(input).upper())

        if name:
            await self.download_by_id(ctx, input)
        else:
            await self.download_by_query(ctx, input)

    @download.error
    async def download_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.", ephemeral=True)
            return
        
    @commands.Cog.listener()
    async def on_config_update(self):
        self.config = load_config()
        self.update_cooldown_mapping()


    async def download_by_id(self, ctx, id: str):
        name, links = get_download_entry(str(id).upper())
        if name:
            embed = discord.Embed(
                title=f"Found farm:",
                color=discord.Color.green()
            )
            server_icon_url = ctx.guild.icon.url if ctx.guild.icon else None
            if server_icon_url:
                embed.set_thumbnail(url=server_icon_url)
            
            user_avatar_url = ctx.author.display_avatar.url if ctx.author.display_avatar else None
            if user_avatar_url:
                embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=user_avatar_url)
            else:
                embed.set_footer(text=f"Requested by {ctx.author.display_name}")

            field_value = f"ID: {id}\n"
            for download_type, link in links.items():
                field_value += f"- {download_type}: {link}\n"
            
            embed.add_field(name=name, value=field_value, inline=False)

            await ctx.respond(embed=embed)
        else:
            error_embed = discord.Embed(
                title="Download ID Not Found",
                description="Sorry, could not find a link for this download id. It might be released at a later point.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=error_embed)

    async def download_by_query(self, ctx, query: str):
        def get_similarity(farm_name, query_words):
            name = farm_name.lower()
            
            if all(word.lower() in name for word in query_words):
                return 100
            
            return fuzz.partial_ratio(query.lower(), name)

        query_words = query.split()

        found_farms = [
            farm for farm in farmdata.get_farms()
            if get_similarity(farm['name'], query_words) >= 75
        ]

        found_farms.sort(key=lambda x: get_similarity(x['name'], query_words), reverse=True)

        if not found_farms:
            await ctx.respond("No farms found matching your query.", ephemeral=True)
            return

        if len(found_farms) > 3:
            await ctx.respond("Too many results found. Please be more specific in your query.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"Found {len(found_farms)} farm{'s' if len(found_farms) > 1 else ''}:",
            color=discord.Color.green()
        )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        footer_text = f"Requested by {ctx.author.display_name}"
        user_avatar_url = ctx.author.display_avatar.url if ctx.author.display_avatar else None
        embed.set_footer(text=footer_text, icon_url=user_avatar_url)

        for farm in found_farms:
            field_value = f"ID: {farm['id']}\n"
            for download_type, link in farm['links'].items():
                field_value += f"- {download_type}: {link}\n"
            embed.add_field(name=farm['name'], value=field_value, inline=False)

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(DownloadCommand(bot))