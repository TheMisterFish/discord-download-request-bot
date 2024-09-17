import discord
from discord.ext import commands
from discord.commands import Option
from discord.ext.commands import CooldownMapping, BucketType

from core.guards import is_not_ignored, in_allowed_channel
from core.database import get_server_database
from core.logger import command_logger
from core.config import load_config

class DownloadCommand(commands.Cog):
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

    async def download_id_autocomplete(self, ctx: discord.AutocompleteContext):
        server_id = ctx.interaction.guild_id
        db = get_server_database(server_id)
        return db.get_matching_download_ids(100, ctx.value)

    async def download_name_autocomplete(self, ctx: discord.AutocompleteContext):
        server_id = ctx.interaction.guild_id
        db = get_server_database(server_id)
        return db.get_download_names(100, ctx.value, 0)

    async def download_id_name_autocomplete(self, ctx: discord.AutocompleteContext):
        server_id = ctx.interaction.guild_id
        db = get_server_database(server_id)
        matches = db.get_download_id_names(25, ctx.value, 50)  # Adjust count and percentage as needed
        return [f"{id} - {name}" for id, name in matches]

    @commands.slash_command(name="download", description="Search for a download by name or ID")
    @is_not_ignored()
    @in_allowed_channel()
    @command_logger
    async def download(
        self,
        ctx,
        name: Option(str, "Enter the download name", autocomplete=download_name_autocomplete, required=False) = None,
        id: Option(str, "Enter the download ID", autocomplete=download_id_autocomplete, required=False) = None
    ):
        await self.check_cooldown(ctx)
        await self.process_download_request(ctx, name, id)

    @commands.slash_command(name="dn", description="Search for a download by name or ID (shortcut)")
    @is_not_ignored()
    @in_allowed_channel()
    @command_logger
    async def dn(
        self,
        ctx,
        input: Option(str, "Enter the download name or ID", autocomplete=download_id_name_autocomplete, required=True)
    ):
        await self.check_cooldown(ctx)
        await self.process_download_request(ctx, input, input)

    async def process_download_request(self, ctx, name, id):
        server_id = ctx.guild.id
        db = get_server_database(server_id)

        if id:
            name, links = db.get_download_entry(id.upper())
            if not name:
                await ctx.respond(f"No download found with ID: {id}", ephemeral=True)
                return
        elif name:
            matching_downloads = db.get_matching_downloads(100, name, 70)
            if not matching_downloads:
                await ctx.respond(f"No downloads found matching '{name}'.", ephemeral=True)
                return
        else:
            await ctx.respond("Please provide either a download name or ID.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Download Search Results",
            color=discord.Color.green()
        )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        footer_text = f"Requested by {ctx.author.display_name}"
        user_avatar_url = ctx.author.display_avatar.url if ctx.author.display_avatar else None
        embed.set_footer(text=footer_text, icon_url=user_avatar_url)

        if id:
            linked_name = f"[{name}]({list(links.values())[0]})"
            embed.add_field(name=linked_name, value=f"ID: {id}", inline=False)
        else:
            if len(matching_downloads) > 3:
                await ctx.respond("Too many results found. Please be more specific in your query.", ephemeral=True)
                return

            for download in matching_downloads[:3]:
                name = download['name']
                links = download['links']
                first_link = next(iter(links.values()))
                linked_name = f"[{name}]({first_link})"
                embed.add_field(name=linked_name, value=f"ID: {download['id']}", inline=False)

        await ctx.respond(embed=embed)

    @download.error
    @dn.error
    async def download_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.", ephemeral=True)
            return

    @commands.Cog.listener()
    async def on_config_update(self, server_id):
        if server_id in self.cooldown_mappings:
            del self.cooldown_mappings[server_id]

def setup(bot):
    bot.add_cog(DownloadCommand(bot))