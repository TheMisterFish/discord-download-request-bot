import csv
import json
import re
import asyncio
import discord
import os

from core.config import DATABASE_FILE

def init_database():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Links'])

def update_database(id: str, name, channel, link):
    id = id.upper()
    rows = []
    updated = False
    with open(DATABASE_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == id:
                links = json.loads(row[2])
                links[channel] = link
                rows.append([id, name, json.dumps(links)])
                updated = True
            else:
                rows.append(row)
    
    if not updated:
        links = {channel: link}
        rows.append([id, name, json.dumps(links)])
    
    with open(DATABASE_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def get_entry(id):
    with open(DATABASE_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == id:
                return row[1], json.loads(row[2])
    return None, None

async def process_message(message):
    match = re.search(r'DN : (.+)', message.content)
    if match:
        id = match.group(1)
        link_match = re.search(r'Link : (https?://\S+)', message.content)
        if link_match:
            mediafire_link = link_match.group(1)
            name = await get_title_from_embed(message)

            if not name:
                name = "Unknown Title"

            update_database(id, name, message.channel.name, message.jump_url)

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
            print(result_message)
    except Exception as e:
        error_message = f"❌ **An error occurred** while scanning {channel.name}: {str(e)}"
        if ctx:
            if ctx.interaction.response.is_done():
                await ctx.followup.send(error_message, ephemeral=True)
            else:
                await ctx.respond(error_message, ephemeral=True)
        else:
            print(error_message)