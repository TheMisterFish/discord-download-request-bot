import re
import asyncio
import discord

from core.database import get_server_database
from core.logger import get_server_logger
from core.config import load_config

def truncate_with_dots(text, max_length=256):
    if len(text) > max_length:
        return text[: max_length - 3] + "..."
    return text
    
async def process_download_message(message):
    server_id = message.guild.id
    config = load_config(server_id)
    search_regex = config.get('search_regex', 'DN : (.+)')

    content_to_check = message.content

    # Check for embeds
    if message.embeds:
        for embed in message.embeds:
            if embed.description:
                content_to_check += "\n" + embed.description

    match = re.search(search_regex, content_to_check)
    if match:
        id = match.group(1)
        download_match = re.search(r'Link : (https?://\S+)', content_to_check)
        if download_match:
            name = await get_title_from_embed(message)

            if not name:
                name = "Unknown Title"

            server_id = message.guild.id
            db = get_server_database(server_id)
            db.update_download_database(id, name, message.channel.name, message.jump_url)

async def process_video_message(message):
    content_to_check = message.content
    video_url = None
    video_title = None

    if message.embeds:
        for embed in message.embeds:
            if embed.type == 'video' and embed.url:
                video_url = embed.url
                video_title = embed.title
            elif embed.type == 'rich' and embed.url and ('youtube.com' in embed.url or 'youtu.be' in embed.url):
                video_url = embed.url
                video_title = embed.title
            
            if embed.description:
                content_to_check += "\n" + embed.description
            if embed.fields:
                for field in embed.fields:
                    content_to_check += f"\n{field.name}: {field.value}"
            
            if video_url and video_title:
                break

    if not video_url:
        youtube_link = re.search(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})', content_to_check)
        if youtube_link:
            video_id = youtube_link.group(6)
            video_url = f"https://www.youtube.com/watch?v={video_id}"

    tag_match = re.search(r'<@&(\d+)>', content_to_check)
    tag = tag_match.group(0) if tag_match else ""

    if video_url:
        name = video_title if video_title else await get_title_from_embed(message)
        if not name:
            name = "Unknown Video Title"

        server_id = message.guild.id
        db = get_server_database(server_id)
        db.update_video_database(name, message.channel.name, message.jump_url, tag)

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

async def scan_download_channel(ctx, channel, server_id=None):
    if server_id is None:
        if ctx and ctx.guild:
            server_id = ctx.guild.id
        else:
            raise ValueError("server_id must be provided if not available in ctx")

    serverLogger = get_server_logger(server_id)
    
    try:
        message_count = 0
        async for message in channel.history(limit=None):
            await process_download_message(message)
            message_count += 1
            
            if message_count % 100 == 0:
                await asyncio.sleep(0)

        result_message = f"✅ Scan finished for channel: **{channel.name}**. Processed **{message_count}** messages."
        serverLogger.logger.info(result_message)
        
        if ctx:
            if ctx.interaction.response.is_done():
                await ctx.followup.send(result_message, ephemeral=True)
            else:
                await ctx.respond(result_message, ephemeral=True)
        else:
            print(f"✅ Scan finished for channel: {channel.name}. Processed {message_count} messages.")
    except Exception as e:
        error_message = f"❌ **An error occurred** while scanning {channel.name}: {str(e)}"
        serverLogger.logger.error(error_message)

        if ctx:
            if ctx.interaction.response.is_done():
                await ctx.followup.send(error_message, ephemeral=True)
            else:
                await ctx.respond(error_message, ephemeral=True)
        else:
            print(f"❌ An error occurred while scanning {channel.name}: {str(e)}")

async def scan_video_channel(ctx, channel, server_id=None):
    if server_id is None:
        if ctx and ctx.guild:
            server_id = ctx.guild.id
        else:
            raise ValueError("server_id must be provided if not available in ctx")

    serverLogger = get_server_logger(server_id)
    
    try:
        message_count = 0
        async for message in channel.history(limit=None):
            await process_video_message(message)
            message_count += 1
            
            if message_count % 100 == 0:
                await asyncio.sleep(0)

        result_message = f"✅ Video scan finished for channel: **{channel.name}**. Processed **{message_count}** messages."
        serverLogger.logger.info(result_message)
        
        if ctx:
            if ctx.interaction.response.is_done():
                await ctx.followup.send(result_message, ephemeral=True)
            else:
                await ctx.respond(result_message, ephemeral=True)
        else:
            print(f"✅ Video scan finished for channel: {channel.name}. Processed {message_count} messages.")
    except Exception as e:
        error_message = f"❌ **An error occurred** while scanning video channel {channel.name}: {str(e)}"
        serverLogger.logger.error(error_message)

        if ctx:
            if ctx.interaction.response.is_done():
                await ctx.followup.send(error_message, ephemeral=True)
            else:
                await ctx.respond(error_message, ephemeral=True)
        else:
            print(f"❌ An error occurred while scanning video channel {channel.name}: {str(e)}")