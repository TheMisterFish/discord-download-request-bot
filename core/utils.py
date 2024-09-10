import re
import asyncio
import discord

from core.datamanager import datamanager
from core.database import update_download_database, update_video_database
from core.logger import logger

async def process_download_message(message):
    match = re.search(r'DN : (.+)', message.content)
    if match:
        id = match.group(1)
        download_match = re.search(r'Link : (https?://\S+)', message.content)
        if download_match:
            name = await get_title_from_embed(message)

            if not name:
                name = "Unknown Title"

            update_download_database(id, name, message.channel.name, message.jump_url)
            datamanager.update_farm(id, name, message.channel.name, message.jump_url)

async def process_video_message(message):
    youtube_link = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})', message.content)
    tag_match = re.search(r'<@&(\d+)>', message.content)
    
    if youtube_link:
        video_id = youtube_link.group(6)
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        name = await get_title_from_embed(message)

        if not name:
            name = "Unknown Video Title"

        tag = tag_match.group(0) if tag_match else ""
        
        update_video_database(name, message.channel.name, message.jump_url, tag)
        datamanager.update_video(name, message.channel.name, message.jump_url, tag)

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

async def scan_download_channel(ctx, channel):
    try:
        message_count = 0
        async for message in channel.history(limit=None):
            await process_download_message(message)
            message_count += 1
            
            if message_count % 100 == 0:
                await asyncio.sleep(0)

        result_message = f"✅ Scan finished for channel: **{channel.name}**. Processed **{message_count}** messages."
        logger.info(result_message)
        
        if ctx:
            if ctx.interaction.response.is_done():
                await ctx.followup.send(result_message, ephemeral=True)
            else:
                await ctx.respond(result_message, ephemeral=True)
        else:
            print(f"✅ Scan finished for channel: {channel.name}. Processed {message_count} messages.")
    except Exception as e:
        error_message = f"❌ **An error occurred** while scanning {channel.name}: {str(e)}"
        logger.error(error_message)

        if ctx:
            if ctx.interaction.response.is_done():
                await ctx.followup.send(error_message, ephemeral=True)
            else:
                await ctx.respond(error_message, ephemeral=True)
        else:
            print(f"❌ An error occurred while scanning {channel.name}: {str(e)}")

async def scan_video_channel(ctx, channel):
    try:
        message_count = 0
        async for message in channel.history(limit=None):
            await process_video_message(message)
            message_count += 1
            
            if message_count % 100 == 0:
                await asyncio.sleep(0)

        result_message = f"✅ Video scan finished for channel: **{channel.name}**. Processed **{message_count}** messages."
        logger.info(result_message)
        
        if ctx:
            if ctx.interaction.response.is_done():
                await ctx.followup.send(result_message, ephemeral=True)
            else:
                await ctx.respond(result_message, ephemeral=True)
        else:
            print(f"✅ Video scan finished for channel: {channel.name}. Processed {message_count} messages.")
    except Exception as e:
        error_message = f"❌ **An error occurred** while scanning video channel {channel.name}: {str(e)}"
        logger.error(error_message)

        if ctx:
            if ctx.interaction.response.is_done():
                await ctx.followup.send(error_message, ephemeral=True)
            else:
                await ctx.respond(error_message, ephemeral=True)
        else:
            print(f"❌ An error occurred while scanning video channel {channel.name}: {str(e)}")

def load_farms():
    return datamanager.get_farms()

async def farm_autocomplete(ctx, farms):
    return [farm['name'] for farm in farms if ctx.value.lower() in farm['name'].lower()]

async def id_autocomplete(ctx, farms):
    return [farm_id for farm_id in farms if ctx.value.upper() in farm_id]

async def farm_name_and_id_autocomplete(ctx, farm_ids, farms):
    user_input = ctx.value.lower()
    
    name_matches = [farm['name'] for farm in farms if user_input in farm['name'].lower()]
    id_matches = [farm_id for farm_id in farm_ids if user_input.upper() in farm_id]
    
    return list(set(name_matches + id_matches))

async def video_title_autocomplete(ctx, videos):
    return [entry[0] for entry in videos if ctx.value.lower() in entry[0].lower()]
