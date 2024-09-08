import re
import asyncio
import discord

from core.farmdata import farmdata
from core.database import update_database

async def process_message(message):
    match = re.search(r'DN : (.+)', message.content)
    if match:
        id = match.group(1)
        link_match = re.search(r'Link : (https?://\S+)', message.content)
        if link_match:
            name = await get_title_from_embed(message)

            if not name:
                name = "Unknown Title"

            update_database(id, name, message.channel.name, message.jump_url)
            farmdata.update_farm(id, name, message.channel.name, message.jump_url)

async def get_title_from_embed(message):
    max_attempts = 10
    delay = 1

    for _ in range(max_attempts):
        if message.embeds:
            embed = message.embeds[0]
            if embed.title:
                return embed.title
        
        await asyncio.sleep(delay)
        try:
            message = await message.channel.fetch_message(message.id)
        except discord.errors.NotFound:
            return None

    return None

async def scan_channel(ctx, channel):
    try:
        message_count = 0
        async for message in channel.history(limit=None):
            await process_message(message)
            message_count += 1
        
        result_message = f"✅ Scan finished for channel: **{channel.name}**. Processed **{message_count}** messages."
        
        if ctx:
            if ctx.interaction.response.is_done():
                await ctx.followup.send(result_message, ephemeral=True)
            else:
                await ctx.respond(result_message, ephemeral=True)
        else:
            print(f"✅ Scan finished for channel: {channel.name}. Processed {message_count} messages.")
    except Exception as e:
        error_message = f"❌ **An error occurred** while scanning {channel.name}: {str(e)}"
        if ctx:
            if ctx.interaction.response.is_done():
                await ctx.followup.send(error_message, ephemeral=True)
            else:
                await ctx.respond(error_message, ephemeral=True)
        else:
            print(f"❌ An error occurred while scanning {channel.name}: {str(e)}")

def load_farms():
    return farmdata.get_farms()

async def farm_autocomplete(ctx, farms):
    return [farm['name'] for farm in farms if ctx.value.lower() in farm['name'].lower()]

async def id_autocomplete(ctx, farms):
    return [farm_id for farm_id in farms if ctx.value.upper() in farm_id]