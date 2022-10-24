import discord

from discord import Interaction, WebhookMessage
from discord.ext import commands

from logingateway import HuTaoLoginAPI
from logingateway.model import Player

from typing import Dict

# Config
CLIENT_ID = "abcd12345"
CLIENT_SECRET = "abcd12345"
TOKEN = "abcd12345"

# Discord
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='>', intents=intents)

# Hu Tao Login Gateway
gateway = HuTaoLoginAPI(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

tokenStore: Dict[str, WebhookMessage] = {}

@gateway.player()
async def player_data(data: Player):
    if not data.token in tokenStore:
        return
    
    ctx = tokenStore[data.token]

    # Recieved data
    print(data.genshin)

    # Send if success
    await ctx.edit(content="🎉 Success to login genshin")

@gateway.ready()
async def ready(data):
    print("Connected to Hu Tao Gateway")

@bot.event
async def on_ready():
    print("Connected")
    try :
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        print("Connecting to Hu Tao Gateway...")
        await gateway.start()
    except Exception as e:
        print(e)
    

@bot.tree.command(name="login", description="Login Genshin account")
async def login_genshin(ctx: Interaction):
    await ctx.response.defer(ephemeral=True)
    url, token = gateway.generate_login_url(
        user_id=str(ctx.user.id),
        guild_id=str(ctx.guild_id),
        channel_id=str(ctx.channel_id),
        language="th"
    )
    
    message = await ctx.followup.send(f"Please login genshin to verify login via link\n{url}")
    tokenStore[token] = message

bot.run(TOKEN)