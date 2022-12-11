import discord

from discord import Interaction, WebhookMessage
from discord.ext import commands

from logingateway import HuTaoLoginAPI
from logingateway.model import Player,AccountCookieToken
from logingateway.api import HuTaoLoginRESTAPI

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

# Hu Tao Login REST API
rest_client=HuTaoLoginRESTAPI(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)


tokenStore: Dict[str, WebhookMessage] = {}
historyStore: Dict[str, str] = {}

@gateway.player()
async def player_data(data: Player):
    ctx = tokenStore[data.token]

    # Recieved data
    print(data.genshin)

    # Send if success
    await ctx.edit(content="🎉 Success to login genshin")

@gateway.player_update()
async def player_update(data: Player):
    # Recieved player update data
    print(data.genshin)

@gateway.ready()
async def ready(data):
    print("Connected to Hu Tao Gateway")

@bot.event
async def on_ready():
    print("Connected")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        print("Connecting to Hu Tao Gateway...")
        await gateway.start()
    except Exception as e:
        print(e)

async def reload_cookies(id:str):
    history  = historyStore[id] if id in historyStore else await rest_client.get_history_user(id,login_type='mail')
    if history.data is not []:
        token = history.data[0].token
        historyStore[id] = token
    else:
        return None 
    new_cookie=await rest_client.reload_new_cookie(id,token)
    return new_cookie


@bot.tree.command(name="login", description="Login Genshin account")
async def login_genshin(ctx: Interaction):
    await ctx.response.defer(ephemeral=True)
    url, token = gateway.generate_login_url(
        user_id=str(ctx.user.id),
        guild_id=str(ctx.guild_id),
        channel_id=str(ctx.channel_id),
        language="en"
    )

    view = discord.ui.View()
    view.add_item(discord.ui.Button(
        url=url,
        label="Login Genshin account"
    ))

    message = await ctx.followup.send(f"Please login genshin to verify login via button", view=view)
    tokenStore[token] = message

@bot.tree.command(name="reload", description="Reload Redeem token")
async def reload_genshin(ctx: Interaction):
    await ctx.response.defer(ephemeral=True)
    new_cookie=await reload_cookies(str(ctx.user.id))
    if new_cookie is not None:
        await ctx.edit_original_response(content=f"Reloaded new cookie")
    else:
        await ctx.edit_original_response(content=f"Failed to reload new cookie you need to login using mail type setup")

    

bot.run(TOKEN)
