import discord

from discord.ext import commands

# Config
TOKEN = ""

# Discord
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='>', intents=intents)

@bot.event
async def on_ready():
    print("Connected")
    try:
        await bot.load_extension("cogs.login")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(type(e))

bot.run(TOKEN)
