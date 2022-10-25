import discord

from discord.ext import commands

# Config
TOKEN = "abcd12345"

# Discord
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='>', intents=intents)

bot.load_extension("cogs.login")

bot.run(TOKEN)
