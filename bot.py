import discord
from dotenv import load_dotenv
import os

from core.database import init_database
from core.logger import logger, log_command

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = discord.Bot(intents=intents)

# Load cogs
bot.load_extension('cogs.events')
bot.load_extension('cogs.downloadCommand')
bot.load_extension('cogs.linkCommand')
bot.load_extension('cogs.ignoreCommand')
bot.load_extension('cogs.logCommand')

# Initialize the bot
init_database()
bot.run(os.getenv('BOT_TOKEN'))