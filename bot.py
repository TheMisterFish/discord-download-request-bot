import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from core.utils import init_database

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = discord.Bot(intents=intents)

# Load cogs
bot.load_extension('cogs.commands')
bot.load_extension('cogs.events')

# Initialize the bot
init_database()
bot.run(os.getenv('BOT_TOKEN'))