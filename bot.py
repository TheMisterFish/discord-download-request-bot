import discord
from discord.ext import commands
from discord.commands import Option
from discord import ApplicationContext
from discord.errors import ApplicationCommandInvokeError

import csv
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = discord.Bot(intents=intents)

# Constants
CONFIG_FILE = 'config.json'
DATABASE_FILE = 'database.csv'

# Load configuration
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {'link_channels': [], 'ignored_users': []}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

# Save configuration
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# Initialize or load the database
def init_database():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Links'])

# Add or update entry in the database
def update_database(id, name, channel, link):
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

# Get entry from the database
def get_entry(id):
    with open(DATABASE_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == id:
                return row[1], json.loads(row[2])
    return None, None

async def process_message(message):
    match = re.search(r'DN : (\d+)', message.content)
    if match:
        id = match.group(1)
        link_match = re.search(r'Link : (https?://\S+)', message.content)
        if link_match:
            mediafire_link = link_match.group(1)
            name = get_title_from_embed(message)

            if not name:
                name = "Unknown Title"

            update_database(id, name, message.channel.name, message.jump_url)

def get_title_from_embed(message):
    if message.embeds:
        embed = message.embeds[0]
        if embed.title:
            return embed.title
    return None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    config = load_config()
    for channel_name in config['link_channels']:
        channel = discord.utils.get(bot.get_all_channels(), name=channel_name)
        if channel:
            await scan_channel(None, channel)
    print('Initialization complete')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    config = load_config()
    if str(message.author.id) in config['ignored_users']:
        return

    if message.channel.name in config['link_channels']:
        await process_message(message)

@bot.slash_command(name="download", description="Search for a download number")
async def download(ctx, number: int):
    name, links = get_entry(str(number))
    if name:
        response = f"Found **{name}**!\n\n"
        for channel, link in links.items():
            response += f"**{channel}** link: {link}\n"
        await ctx.respond(response)
    else:
        await ctx.respond("Sorry, could not find a link for this download number.")

@bot.slash_command(name="ignore", description="Ignore a user")
@commands.has_permissions(administrator=True)
async def ignore(ctx, user: discord.Member):
    config = load_config()
    if str(user.id) not in config['ignored_users']:
        config['ignored_users'].append(str(user.id))
        save_config(config)
        await ctx.respond(f"✅ Now ignoring user: **{user.name}**", ephemeral=True)
    else:
        await ctx.respond(f"Already ignoring user: **{user.name}**", ephemeral=True)

@bot.slash_command(name="linkchannel", description="Manage link channels")
@commands.has_permissions(administrator=True)
async def linkchannel(
    ctx, 
    action: Option(str, "Choose an action", choices=["add", "remove", "scan"]),
    channel: Option(discord.TextChannel, "Select a channel", required=False) = None
):
    config = load_config()

    if action == "add":
        if channel:
            if channel.name not in config['link_channels']:
                config['link_channels'].append(channel.name)
                save_config(config)
                await ctx.respond(f"✅ Added **{channel.name}** to link channels")
            else:
                await ctx.respond(f"**{channel.name}** is already a link channel")
        else:
            await ctx.respond("Please specify a channel to add.")
    elif action == "remove":
        if channel:
            if channel.name in config['link_channels']:
                config['link_channels'].remove(channel.name)
                save_config(config)
                await ctx.respond(f"✅ Removed **{channel.name}** from link channels")
            else:
                await ctx.respond(f"**{channel.name}** is not a link channel")
        else:
            await ctx.respond("Please specify a channel to remove.")
    elif action == "scan":
        if channel:
            await ctx.respond(f"🔍 Scanning channel **{channel}**", ephemeral=True)
            await scan_channel(ctx, channel)
        else:
            await ctx.respond("🔍 Scanning all configured channels...", ephemeral=True)
            for channel_name in config['link_channels']:
                channel = discord.utils.get(ctx.guild.channels, name=channel_name)
                if channel:
                    await scan_channel(ctx, channel)
                else:
                    await ctx.followup.send(f"❌ Could not find channel: **{channel_name}**", ephemeral=True)
            await ctx.followup.send("✅ Scan completed for all configured channels.", ephemeral=True)

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

# Initialize the bot
init_database()
bot.run(os.getenv('BOT_TOKEN'))