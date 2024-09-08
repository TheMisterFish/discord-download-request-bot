import discord
from discord.ext import commands
from discord.commands import Option

from fuzzywuzzy import fuzz, process

from core.guards import is_not_ignored
from core.utils import farm_autocomplete
from core.database import get_entry
from core.farmdata import farmdata

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def farm_name_autocomplete(self, ctx: discord.AutocompleteContext):
        return await farm_autocomplete(ctx, farmdata.get_farms())

    @commands.slash_command(name="download", description="Search for a farm by name or ID")
    @is_not_ignored()
    async def download(
        self,
        ctx,
        query: Option(str, "Enter the farm name or ID", autocomplete=farm_name_autocomplete, required=False) = None,
        id: Option(str, "Enter the download ID", required=False) = None
    ):
        if id:
            await self.download_by_id(ctx, id)
        elif query:
            await self.download_by_query(ctx, query)
        else:
            await ctx.respond("Please provide either a farm name or an ID.", ephemeral=True)

    async def download_by_id(self, ctx, id: str):
        name, links = get_entry(str(id).upper())
        if name:
            embed = discord.Embed(
                title=f"{name}",
                color=discord.Color.green()
            )
            
            field_value = f"ID: {id}\n\n"
            for link_type, link in links.items():
                field_value += f"{link_type}: {link}\n"
            
            embed.description = field_value
            
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

        for farm in found_farms:
            field_value = f"ID: {farm['id']}\n"
            for link_type, link in farm['links'].items():
                field_value += f"- {link_type}: {link}\n"
            embed.add_field(name=farm['name'], value=field_value, inline=False)

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Commands(bot))