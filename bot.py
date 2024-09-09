import discord
from dotenv import load_dotenv
import os

from core.database import init_database
from core.config import create_config
from core.logger import logger, log_command

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = discord.Bot(intents=intents)

# Load cogs
# Event listener
bot.load_extension('cogs.events')

# Download command
bot.load_extension('cogs.downloadCommand')

# Moderator commands
bot.load_extension('cogs.linkCommand')
bot.load_extension('cogs.ignoreCommand')
bot.load_extension('cogs.logCommand')
bot.load_extension('cogs.allowDownloadCommand')
bot.load_extension('cogs.configCommand')
bot.load_extension('cogs.helpCommand')

# Initialize the bot
init_database()
create_config()

bot.run(os.getenv('BOT_TOKEN'))