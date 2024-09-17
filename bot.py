import discord
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = discord.Bot(intents=intents)

# Load cogs
# Event listener
bot.load_extension('cogs.events')

# User command
bot.load_extension('cogs.downloadCommand')
bot.load_extension('cogs.videoCommand')

# Moderator commands
bot.load_extension('cogs.downloadChannelCommand')
bot.load_extension('cogs.videoChannelCommand')
bot.load_extension('cogs.ignoreCommand')
bot.load_extension('cogs.logCommand')
bot.load_extension('cogs.allowDownloadCommand')
bot.load_extension('cogs.configCommand')
bot.load_extension('cogs.helpCommand')
# bot.load_extension('cogs.creditCommand') -> TODO make nicer
 
bot.run(os.getenv('BOT_TOKEN'))